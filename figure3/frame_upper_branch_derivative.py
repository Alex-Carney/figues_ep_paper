from scipy.ndimage import gaussian_filter1d
import matplotlib.pyplot as plt
import numpy as np

from figure3.config import LABEL_FONT_SIZE, TICK_FONT_SIZE, \
    VOLTS_TO_MUT, VEC_B, SAVE_DPI, UPPER_BRANCH_LINE_COLOR, UPPER_BRANCH_FREQ_LINE, LEGEND_FONT_SIZE_DERIVATIVES


def generate(ax_main, power_grid, voltages, frequencies, ax_ep_derivative=None, ax_ep_power=None, save_plot=False):

    # Find the index of the closest frequency to FREQ_LINE in frequencies
    freq_idx = (np.abs(frequencies - UPPER_BRANCH_FREQ_LINE)).argmin()
    trace_power = power_grid[:, freq_idx]

    # Calculate and smooth the trace power using Gaussian smoothing
    smoothed_power = gaussian_filter1d(trace_power, sigma=1)  # Apply Gaussian smoothing with a standard deviation of 1
    d_power_d_voltage = np.abs(np.gradient(smoothed_power, voltages))  # Take the absolute derivative

    # Primary Y-axis (Abs(dPower/dVoltage) vs. Voltage) - Left axis

    deriv_color = 'purple'

    deriv_label = '|d$S_{21}$/dV|'
    line1, = ax_main.plot(voltages * VOLTS_TO_MUT, d_power_d_voltage, color=deriv_color, linestyle='-',
                          label=deriv_label + '(f = $f_{UB}$)', linewidth=2.5)
    ax_main.set_xlabel('$\Delta$' + VEC_B + '[$\mu$T]', fontsize=LABEL_FONT_SIZE)
    ax_main.set_ylabel(deriv_label + ' [dB/V]', fontsize=LABEL_FONT_SIZE, color=deriv_color)
    ax_main.tick_params(axis='y', labelcolor=deriv_color, labelsize=TICK_FONT_SIZE)
    ax_main.tick_params(axis='x', labelsize=TICK_FONT_SIZE)

    # Secondary Y-axis (Power vs. Voltage) - Right axis
    ax4_dual = ax_main.twinx()
    line2, = ax4_dual.plot(voltages * VOLTS_TO_MUT, trace_power, color=UPPER_BRANCH_LINE_COLOR, label='$S_{21}$(f = $f_{UB}$)',
                           linewidth=3)
    ax4_dual.set_ylabel('$S_{21}$ [dB]', fontsize=LABEL_FONT_SIZE, color=UPPER_BRANCH_LINE_COLOR)
    ax4_dual.tick_params(axis='y', labelcolor=UPPER_BRANCH_LINE_COLOR, labelsize=TICK_FONT_SIZE)

    # Combined legend for both lines and the EP line
    lines = [line1, line2]
    labels = [line.get_label() for line in lines]
    ax_main.legend(lines, labels, loc='upper left', fontsize=LEGEND_FONT_SIZE_DERIVATIVES)

    ax_main.set_ylim([500, 1000])
    ax4_dual.set_ylim([-25, 15])

    if ax_ep_derivative is not None:
        # set the ylim to the same
        ax_main.set_ylim(ax_ep_derivative.get_ylim())
        # and the xlim
        ax_main.set_xlim(ax_ep_derivative.get_xlim())

    if ax_ep_power is not None:
        # set the ylim to the same
        ax4_dual.set_ylim(ax_ep_power.get_ylim())
        # and the xlim
        ax4_dual.set_xlim(ax_ep_power.get_xlim())

    if save_plot:
        plt.tight_layout()
        plt.savefig('frame_derivative_upper.png', dpi=SAVE_DPI)





# Driver code for standalone testing
if __name__ == "__main__":
    # Third plot (Transmission Plot) - Top Right with Inset
    from shared import generate_transmission_plots as gte

    experiment_id = '413b3b49-c536-427f-a0fd-f0859052f0bd'  # Set the experiment ID
    engine = gte.__get_engine(
        '../data/overweekend_loop_phase_search')  # Ensure correct database name and engine creation
    power_grid, voltages, frequencies, settings = gte.__get_data_from_db(engine, experiment_id)

    fig, ax_main = plt.subplots(figsize=(10, 6))
    generate(ax_main, power_grid, voltages, frequencies)
    plt.tight_layout()
    plt.savefig('frame_derivative_upper.png', dpi=SAVE_DPI)
