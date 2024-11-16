# frame_C.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from sqlalchemy import create_engine
from scipy.signal import find_peaks
from config import LABEL_FONT_SIZE, TICK_FONT_SIZE, LEGEND_FONT_SIZE, \
    INSET_TICK_FONT_SIZE, INSET_LABEL_FONT_SIZE, set_y_ticks  # Assuming config file for shared settings
import matplotlib.ticker as mticker
from matplotlib.colors import ListedColormap

TABLE_NAME = 'expr'

# Thresholds mapping based on loop attenuation
attenuation_thresholds = {
    17.0: 15.9,
    16.5: 15.1,
    16.0: 14.6,
    15.5: 14.6,
    15.0: 14.1,
    14.5: 14.0
}


# Helper functions
def __get_engine(db_name):
    return create_engine(f'sqlite:///../data/{db_name}.db')


def __get_data_from_db(engine, experiment_id, freq_min=1e9, freq_max=99e9):
    data_query = f"""
    SELECT frequency_hz, set_cavity_fb_att, power_dBm FROM {TABLE_NAME}
    WHERE experiment_id = '{experiment_id}'
    AND frequency_hz BETWEEN {freq_min} AND {freq_max}
    ORDER BY set_cavity_fb_att, frequency_hz
    """
    data = pd.read_sql_query(data_query, engine)
    if not data.empty:
        pivot_table = data.pivot_table(index='set_cavity_fb_att', columns='frequency_hz', values='power_dBm',
                                       aggfunc='first')
        attenuations = pivot_table.index.values
        frequencies = pivot_table.columns.values
        power_grid = pivot_table.values
        return power_grid, attenuations, frequencies
    else:
        return None, None, None


def __default_peak_finding_function(frequencies, powers):
    peaks_indices, properties = find_peaks(powers, height=-7, prominence=0.037, distance=10)
    peak_freqs = frequencies[peaks_indices]
    peak_powers = powers[peaks_indices]
    return peak_freqs, peak_powers


def __process_all_traces(power_grid, attenuations, frequencies, peak_finding_function=__default_peak_finding_function):
    attenuations_list = []
    peak_freqs_list = []
    peak_powers_list = []
    for idx, attenuation in enumerate(attenuations):
        powers = power_grid[idx, :]
        peak_freqs, peak_powers = peak_finding_function(frequencies, powers)
        attenuations_list.extend([attenuation] * len(peak_freqs))
        peak_freqs_list.extend(peak_freqs)
        peak_powers_list.extend(peak_powers)
    peaks_df = pd.DataFrame(
        {'attenuation': attenuations_list, 'peak_freq': peak_freqs_list, 'peak_power': peak_powers_list})
    return peaks_df


# Main function to generate Frame C
def generate(ax):
    # Load data
    dbs = ['loop_14.5_dB_1', 'loop_15.5_dB_1', 'loop_16.5_dB_1', 'loop_17_dB_1']
    all_peaks = pd.DataFrame()
    colors = {'loop_14.5_dB_1': 'crimson', 'loop_15.5_dB_1': '#483D8B', 'loop_16.5_dB_1': 'royalblue',
              'loop_17_dB_1': 'forestgreen'}

    for db_name in dbs:
        engine = __get_engine(db_name)
        experiment_ids = pd.read_sql_query(f'SELECT DISTINCT experiment_id FROM {TABLE_NAME}', engine)
        for experiment_id in experiment_ids['experiment_id']:
            power_grid, attenuations, frequencies = __get_data_from_db(engine, experiment_id)
            if power_grid is not None:
                peaks_df = __process_all_traces(power_grid, attenuations, frequencies)
                settings = pd.read_sql_query(
                    f"SELECT set_loop_phase_deg, set_loop_att, set_loopback_att, set_yig_fb_phase_deg, set_voltage, set_yig_fb_att FROM {TABLE_NAME} WHERE experiment_id = '{experiment_id}'",
                    engine).iloc[0]
                loop_att = settings['set_loop_att']
                threshold = attenuation_thresholds.get(loop_att, max(attenuations))
                filtered_peaks_df = peaks_df[peaks_df['attenuation'] > threshold].copy()
                filtered_peaks_df['database'] = db_name
                all_peaks = pd.concat([all_peaks, filtered_peaks_df], ignore_index=True)

    # Format for labels
    def format_label(db_name):
        return rf"$\Gamma$ = {db_name.split('_')[1]} dB"

    # Main Plot (Peak Positions)
    for name, group in all_peaks.groupby('database'):
        label = format_label(name)
        ax.scatter(group['attenuation'], group['peak_freq'] / 1e9, label=label, s=15, color=colors[name])
    # ax.set_ylabel('Readout Frequency [GHz]', fontsize=LABEL_FONT_SIZE)
    ax.legend(fontsize=LEGEND_FONT_SIZE, loc='upper right')
    ax.tick_params(axis='both', labelsize=TICK_FONT_SIZE)
    # ax.axvline(x=14.1, color='black', linestyle='--', lw=3.0, alpha=0.5)
    # ax.axvline(x=14.7, color='black', linestyle='--', lw=3.0, alpha=0.5)
    # ax.axvline(x=15.3, color='black', linestyle='--', lw=3.0, alpha=0.5)
    # ax.axvline(x=16.0, color='black', linestyle='--', lw=3.0, alpha=0.5)
    # ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: r'$%.3f$' % x))

    # Inset Plot (Frequency Differences)
    inset_ax = inset_axes(ax, width="35%", height="35%", loc="upper left", bbox_to_anchor=(.01, 0, 1, 1),
                          bbox_transform=ax.transAxes)
    legend_labels = set()
    for name, group in all_peaks.groupby('database'):
        group = group.sort_values(by='attenuation')
        grouped = group.groupby('attenuation')
        for attenuation, group_att in grouped:
            freqs = sorted(group_att['peak_freq'])
            diffs = [freqs[i + 1] - freqs[i] for i in range(len(freqs) - 1)]
            if diffs:
                label = format_label(name) if name not in legend_labels else None
                inset_ax.scatter([attenuation] * len(diffs), np.array(diffs) / 1e6, s=15, color=colors[name],
                                 label=label)
                if label:
                    legend_labels.add(name)
    # inset_ax.set_xlabel('$\Gamma_c$ [dB]', fontsize=LABEL_FONT_SIZE - 4)
    # inset_ax.set_ylabel('Frequency Splitting [MHz]', fontsize=LABEL_FONT_SIZE - 4)
    # inset_ax.axvline(x=14.1, color='black', linestyle='--', lw=2.0, alpha=0.5)
    # inset_ax.axvline(x=14.7, color='black', linestyle='--', lw=2.0, alpha=0.5)
    # inset_ax.axvline(x=15.3, color='black', linestyle='--', lw=2.0, alpha=0.5)
    # inset_ax.axvline(x=16.0, color='black', linestyle='--', lw=2.0, alpha=0.5)
    # inset_ax.legend(fontsize=TICK_FONT_SIZE - 2)

    inset_ax.yaxis.set_label_position("right")
    inset_ax.yaxis.tick_right()
    inset_ax.set_ylabel('Splitting (MHz)', fontsize=INSET_LABEL_FONT_SIZE)

    inset_ax.tick_params(axis='both', labelsize=INSET_TICK_FONT_SIZE)

    ax.set_ylim([5.994, 6.009])
    ax.set_xlabel('Attenuation (dB)', fontsize=LABEL_FONT_SIZE)

    set_y_ticks(ax)

    return ax


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(10, 6))
    generate(ax)
    plt.show()
