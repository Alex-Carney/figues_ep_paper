from scipy.ndimage import gaussian_filter1d
import matplotlib.pyplot as plt
import numpy as np

from figure3.config import (
    FREQ_LINE, FREQ_LINE_COLOR, LABEL_FONT_SIZE, VOLTAGE_LINE, EP_LINE_COLOR,
    TICK_FONT_SIZE, VOLTS_TO_MUT, SAVE_DPI, LEGEND_FONT_SIZE_DERIVATIVES,
    UPPER_BRANCH_LINE_COLOR, UPPER_BRANCH_FREQ_LINE
)
from shared.constants import VEC_B


def compute_trace_and_derivative(power_grid, voltages, frequencies, target_freq):
    # Find the index of the closest frequency to target_freq in frequencies
    freq_idx = (np.abs(frequencies - target_freq)).argmin()
    trace_power = power_grid[:, freq_idx]
    # Calculate and smooth the trace power using Gaussian smoothing
    smoothed_power = gaussian_filter1d(trace_power, sigma=1)
    d_power_d_voltage = np.abs(np.gradient(smoothed_power, voltages))
    return trace_power, d_power_d_voltage


def generate(power_grid, voltages, frequencies, save_plot=False):
    # Compute trace and derivative for FREQ_LINE (EP)
    trace_power_ep, d_power_d_voltage_ep = compute_trace_and_derivative(
        power_grid, voltages, frequencies, FREQ_LINE
    )

    # Compute trace and derivative for UPPER_BRANCH_FREQ_LINE (UB)
    trace_power_ub, d_power_d_voltage_ub = compute_trace_and_derivative(
        power_grid, voltages, frequencies, UPPER_BRANCH_FREQ_LINE
    )

    # Create subplots
    fig, (ax_top, ax_bottom) = plt.subplots(2, 1, sharex=True, figsize=(10, 8))

    # Plot the traces on the top subplot
    line1, = ax_top.plot(
        voltages * VOLTS_TO_MUT, trace_power_ep, color=FREQ_LINE_COLOR,
        label='$S_{21}$(f = $f_{EP}$)', linewidth=3
    )
    line2, = ax_top.plot(
        voltages * VOLTS_TO_MUT, trace_power_ub, color=UPPER_BRANCH_LINE_COLOR,
        label='$S_{21}$(f = $f_{UB}$)', linewidth=3
    )

    # EP line on top plot
    ep_line_top = ax_top.axvline(
        x=VOLTAGE_LINE * VOLTS_TO_MUT, color=EP_LINE_COLOR, linestyle='--',
        linewidth=3, alpha=0.7, label="EP line"
    )

    # Set labels and legends for top plot
    ax_top.set_ylabel('$S_{21}$ [dB]', fontsize=LABEL_FONT_SIZE)
    ax_top.tick_params(axis='y', labelsize=TICK_FONT_SIZE)
    ax_top.tick_params(axis='x', labelsize=TICK_FONT_SIZE)
    lines_top = [line1, line2, ep_line_top]
    labels_top = [line.get_label() for line in lines_top]
    ax_top.legend(lines_top, labels_top, loc='upper left', fontsize=LEGEND_FONT_SIZE_DERIVATIVES)

    # Plot the derivatives on the bottom subplot
    line3, = ax_bottom.plot(
        voltages * VOLTS_TO_MUT, d_power_d_voltage_ep, color='crimson',
        linestyle='-', label='|d$S_{21}$/$dB_z$|(f = $f_{EP}$)', linewidth=2.5
    )
    line4, = ax_bottom.plot(
        voltages * VOLTS_TO_MUT, d_power_d_voltage_ub, color='purple',
        linestyle='-', label='|d$S_{21}$/$dB_z$|(f = $f_{UB}$)', linewidth=2.5
    )

    # Add EP line on the derivative plot
    ep_line_bottom = ax_bottom.axvline(
        x=VOLTAGE_LINE * VOLTS_TO_MUT, color=EP_LINE_COLOR, linestyle='--',
        linewidth=3, alpha=0.7, label="EP line"
    )

    # Set labels and legends for bottom plot
    ax_bottom.set_xlabel('$\Delta$' + VEC_B + '[$\mu$T]', fontsize=LABEL_FONT_SIZE)
    ax_bottom.set_ylabel('|d$S_{21}$/$dB_z$| [dB/$\mu$T]', fontsize=LABEL_FONT_SIZE)
    ax_bottom.tick_params(axis='y', labelsize=TICK_FONT_SIZE)
    ax_bottom.tick_params(axis='x', labelsize=TICK_FONT_SIZE)
    lines_bottom = [line3, line4, ep_line_bottom]
    labels_bottom = [line.get_label() for line in lines_bottom]
    ax_bottom.legend(lines_bottom, labels_bottom, loc='upper left', fontsize=LEGEND_FONT_SIZE_DERIVATIVES)

    # Save plot if requested
    if save_plot:
        plt.tight_layout()
        plt.savefig('combined_plot.png', dpi=SAVE_DPI)

    return fig, ax_top, ax_bottom


# Driver code for standalone testing
if __name__ == "__main__":
    from shared import generate_transmission_plots as gte

    experiment_id = '413b3b49-c536-427f-a0fd-f0859052f0bd'  # Set the experiment ID
    engine = gte.__get_engine(
        '../data/overweekend_loop_phase_search'
    )  # Ensure correct database name and engine creation
    power_grid, voltages, frequencies, settings = gte.__get_data_from_db(engine, experiment_id)

    generate(power_grid, voltages, frequencies, save_plot=True)
    plt.show()
