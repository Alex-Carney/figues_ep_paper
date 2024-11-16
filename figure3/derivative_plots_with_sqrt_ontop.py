import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import os
import numpy as np
from scipy.signal import find_peaks

TABLE_NAME = 'expr'

LABEL_FONT_SIZE = 19
TICK_FONT_SIZE = 15
SAVE_DPI = 400


####
# SETTINGS
####


def __get_engine(db_name):
    return create_engine(f'sqlite:///{db_name}.db')


def __get_data_from_db(engine, experiment_id, freq_min=1e9, freq_max=99e9, voltage_min=-2.0, voltage_max=2.0):
    # Query the apparatus settings for the experiment
    settings_query = f"""
    SELECT DISTINCT set_loop_phase_deg, set_loop_att, set_loopback_att,
                    set_cavity_fb_phase_deg, set_cavity_fb_att,
                    set_yig_fb_phase_deg, set_yig_fb_att
    FROM {TABLE_NAME}
    WHERE experiment_id = '{experiment_id}'
    """
    settings = pd.read_sql_query(settings_query, engine).iloc[0]

    # Query the measurement data
    data_query = f"""
    SELECT frequency_hz, set_voltage, power_dBm FROM {TABLE_NAME}
    WHERE experiment_id = '{experiment_id}'
    AND set_voltage BETWEEN {voltage_min} AND {voltage_max}
    AND frequency_hz BETWEEN {freq_min} AND {freq_max}
    ORDER BY set_voltage, frequency_hz
    """
    data = pd.read_sql_query(data_query, engine)

    pivot_table = data.pivot_table(index='set_voltage', columns='frequency_hz', values='power_dBm', aggfunc='first')

    frequencies = pivot_table.columns.values
    voltages = pivot_table.index.values
    power_grid = pivot_table.values

    return power_grid, voltages, frequencies, settings


def __default_peak_finding_function(frequencies, powers):
    peaks_indices, properties = find_peaks(powers, height=-7, prominence=0.025, distance=10)
    peak_freqs = frequencies[peaks_indices]
    peak_powers = powers[peaks_indices]
    return peak_freqs, peak_powers


def __process_all_traces(power_grid, voltages, frequencies, peak_finding_function=__default_peak_finding_function):
    voltages_list = []
    peak_freqs_list = []
    peak_powers_list = []
    for idx, voltage in enumerate(voltages):
        powers = power_grid[idx, :]
        peak_freqs, peak_powers = peak_finding_function(frequencies, powers)
        voltages_list.extend([voltage] * len(peak_freqs))
        peak_freqs_list.extend(peak_freqs)
        peak_powers_list.extend(peak_powers)
    peaks_df = pd.DataFrame({'voltage': voltages_list, 'peak_freq': peak_freqs_list, 'peak_power': peak_powers_list})
    return peaks_df


def __generate_transmission_plot(power_grid, voltages, frequencies, peaks_df, experiment_id, settings, vmin=-40, vmax=8):
    fig, ax = plt.subplots(figsize=(10, 6))

    c = ax.pcolormesh(voltages, frequencies / 1e9, power_grid.T, shading='auto', cmap='inferno', vmin=vmin, vmax=vmax)
    cbar = fig.colorbar(c, ax=ax, label='Power (dBm)', pad=.02)

    # Overlay peak positions
    # s is size
    ax.scatter(peaks_df['voltage'], peaks_df['peak_freq'] / 1e9, color='white', s=1, label='Peak Positions')


    # Add apparatus settings to the title
    title = (f"Experiment ID: {experiment_id}\n"
             f"Loop Phase: {settings['set_loop_phase_deg']}°, Loop Att: {settings['set_loop_att']} dB, "
             f"Loopback Att: {settings['set_loopback_att']} dB\n"
             f"Cavity FB Phase: {settings['set_cavity_fb_phase_deg']}°, Cavity FB Att: {settings['set_cavity_fb_att']} dB, "
             f"YIG FB Phase: {settings['set_yig_fb_phase_deg']}°, YIG FB Att: {settings['set_yig_fb_att']} dB")

    ax.set_title(title)
    ax.set_xlabel('Voltage (V)', fontsize=LABEL_FONT_SIZE)
    ax.set_ylabel('Readout Frequency (GHz)', fontsize=LABEL_FONT_SIZE)
    cbar.set_label('Power (dB)', fontsize=LABEL_FONT_SIZE)

    ax.tick_params(axis='x', labelsize=TICK_FONT_SIZE)
    ax.tick_params(axis='y', labelsize=TICK_FONT_SIZE)
    cbar.ax.tick_params(labelsize=TICK_FONT_SIZE)

    if ax.get_legend_handles_labels()[0]:
        ax.legend()

    plt.tight_layout()
    return fig


def __generate_derivative_plot(power_grid, voltages, frequencies, peaks_df, experiment_id, settings, vmin=0, vmax=None):
    # Compute the absolute value of the derivative of power with respect to voltage
    dPower_dVoltage = np.log(np.abs(np.gradient(power_grid, voltages, axis=0)))

    fig, ax = plt.subplots(figsize=(10, 6))

    c = ax.pcolormesh(voltages, frequencies / 1e9, dPower_dVoltage.T, shading='auto', cmap='inferno', vmin=vmin, vmax=vmax)
    cbar = fig.colorbar(c, ax=ax, label='Log |dPower/dVoltage|', pad=.02)

    # Overlay peak positions
    # s is size
    ax.scatter(peaks_df['voltage'], peaks_df['peak_freq'] / 1e9, color='white', s=1, label='Peak Positions')

    # Add apparatus settings to the title
    title = (f"Absolute Derivative Plot with Peaks - Experiment ID: {experiment_id}\n"
             f"Loop Phase: {settings['set_loop_phase_deg']}°, Loop Att: {settings['set_loop_att']} dB, "
             f"Loopback Att: {settings['set_loopback_att']} dB\n"
             f"Cavity FB Phase: {settings['set_cavity_fb_phase_deg']}°, Cavity FB Att: {settings['set_cavity_fb_att']} dB, "
             f"YIG FB Phase: {settings['set_yig_fb_phase_deg']}°, YIG FB Att: {settings['set_yig_fb_att']} dB")

    ax.set_title(title)
    ax.set_xlabel('Voltage (V)', fontsize=LABEL_FONT_SIZE)
    ax.set_ylabel('Readout Frequency (GHz)', fontsize=LABEL_FONT_SIZE)
    cbar.set_label('|dPower/dVoltage|', fontsize=LABEL_FONT_SIZE)

    ax.tick_params(axis='x', labelsize=TICK_FONT_SIZE)
    ax.tick_params(axis='y', labelsize=TICK_FONT_SIZE)
    cbar.ax.tick_params(labelsize=TICK_FONT_SIZE)

    plt.legend(loc='upper right', fontsize=TICK_FONT_SIZE)
    plt.tight_layout()
    return fig


def __save_plot_to_file(fig, db_name, experiment_id):
    directory = f"VER5.0_{db_name}_colorplots_monday_overnight"
    if not os.path.exists(directory):
        os.makedirs(directory)
    plt.savefig(f'{directory}/transmission_plot_experiment_{experiment_id}.png', dpi=SAVE_DPI, transparent=False,
                facecolor='white')
    plt.close(fig)


def __save_derivative_plot_to_file(fig, db_name, experiment_id):
    directory = f"VER5.0_{db_name}_derivative_plots_monday_overnight"
    if not os.path.exists(directory):
        os.makedirs(directory)
    plt.savefig(f'{directory}/derivative_plot_experiment_{experiment_id}.png', dpi=SAVE_DPI, transparent=False,
                facecolor='white')
    plt.close(fig)


def plot_all_experiments(db_name, freq_min=1e9, freq_max=99e9, voltage_min=-2.0, voltage_max=2.0,
                         vmin_transmission=-40, vmax_transmission=None,
                         vmin_derivative=0, vmax_derivative=None):
    engine = __get_engine(db_name)
    experiment_ids = pd.read_sql_query(f'SELECT DISTINCT experiment_id FROM {TABLE_NAME}', engine)

    for experiment_id in experiment_ids['experiment_id']:
        print(f'Plotting experiment {experiment_id}...')
        power_grid, voltages, frequencies, settings = __get_data_from_db(
            engine, experiment_id, freq_min, freq_max, voltage_min, voltage_max)

        # Process all traces to find peaks
        peaks_df = __process_all_traces(power_grid, voltages, frequencies)

        # Generate transmission plot
        fig = __generate_transmission_plot(power_grid, voltages, frequencies, peaks_df, experiment_id, settings,
                                           vmin=vmin_transmission, vmax=vmax_transmission)
        __save_plot_to_file(fig, db_name, experiment_id)

        # Generate derivative plot with peak positions
        fig_derivative = __generate_derivative_plot(power_grid, voltages, frequencies, peaks_df,
                                                    experiment_id, settings,
                                                    vmin=vmin_derivative, vmax=vmax_derivative)
        __save_derivative_plot_to_file(fig_derivative, db_name, experiment_id)


def plot_experiment(experiment_id, db_name, freq_min=1e9, freq_max=5e9, voltage_min=-2.0, voltage_max=2.0,
                    vmin_transmission=-40, vmax_transmission=8,
                    vmin_derivative=0, vmax_derivative=None):
    engine = __get_engine(db_name)
    power_grid, voltages, frequencies, settings = __get_data_from_db(
        engine, experiment_id, freq_min, freq_max, voltage_min, voltage_max)

    # Process all traces to find peaks
    peaks_df = __process_all_traces(power_grid, voltages, frequencies)

    # Generate transmission plot
    fig = __generate_transmission_plot(power_grid, voltages, frequencies, experiment_id, settings,
                                       vmin=vmin_transmission, vmax=vmax_transmission)
    __save_plot_to_file(fig, db_name, experiment_id)

    # Generate derivative plot with peak positions
    fig_derivative = __generate_derivative_plot(power_grid, voltages, frequencies, peaks_df,
                                                experiment_id, settings,
                                                vmin=vmin_derivative, vmax=vmax_derivative)
    __save_derivative_plot_to_file(fig_derivative, db_name, experiment_id)


if __name__ == "__main__":
    db_name = 'overweekend_loop_phase_search'
    plot_all_experiments(db_name=db_name,
                         freq_min=5.996e9,
                         freq_max=6.04e9,
                         voltage_min=-0.2,
                         voltage_max=0.25,
                         vmin_transmission=-20,
                         vmin_derivative=0,)
