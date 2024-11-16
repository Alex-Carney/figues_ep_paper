from scipy.ndimage import gaussian_filter1d
import matplotlib.pyplot as plt
import numpy as np

from figure3.config import FREQ_LINE, FREQ_LINE_COLOR, LABEL_FONT_SIZE, VOLTAGE_LINE, EP_LINE_COLOR, TICK_FONT_SIZE


def generate(ax_main, power_grid, voltages, frequencies):

    # Find the index of the closest frequency to FREQ_LINE in frequencies
    freq_idx = (np.abs(frequencies - FREQ_LINE)).argmin()
    trace_power = power_grid[:, freq_idx]

    # Calculate and smooth the trace power using Gaussian smoothing
    smoothed_power = gaussian_filter1d(trace_power, sigma=1)  # Apply Gaussian smoothing with a standard deviation of 1
    d_power_d_voltage = np.abs(np.gradient(smoothed_power, voltages))  # Take the absolute derivative

    # Primary Y-axis (Abs(dPower/dVoltage) vs. Voltage) - Left axis

    deriv_color = 'crimson'

    deriv_label = '|d$S_{21}$/dV|'
    line1, = ax_main.plot(voltages, d_power_d_voltage, color=deriv_color, linestyle='-', label=deriv_label + '(f = $f_c$)', linewidth=2.5)
    ax_main.set_xlabel('Voltage [V]', fontsize=LABEL_FONT_SIZE)
    ax_main.set_ylabel(deriv_label + ' [dB/V]', fontsize=LABEL_FONT_SIZE, color=deriv_color)
    ax_main.tick_params(axis='y', labelcolor=deriv_color, labelsize=TICK_FONT_SIZE)
    ax_main.tick_params(axis='x', labelsize=TICK_FONT_SIZE)
    ep_line = ax_main.axvline(x=VOLTAGE_LINE, color=EP_LINE_COLOR, linestyle='--', linewidth=3, alpha=0.7, label="EP line")

    # Secondary Y-axis (Power vs. Voltage) - Right axis
    ax4_dual = ax_main.twinx()
    line2, = ax4_dual.plot(voltages, trace_power, color=FREQ_LINE_COLOR, label='$S_{21}$(f = $f_c$)',
                           linewidth=3)
    ax4_dual.set_ylabel('$S_{21}$ [dB]', fontsize=LABEL_FONT_SIZE, color=FREQ_LINE_COLOR)
    ax4_dual.tick_params(axis='y', labelcolor=FREQ_LINE_COLOR, labelsize=TICK_FONT_SIZE)

    # Combined legend for both lines and the EP line
    lines = [line1, line2, ep_line]
    labels = [line.get_label() for line in lines]
    ax_main.legend(lines, labels, loc='upper left', fontsize=TICK_FONT_SIZE - 2)

# Driver code for standalone testing
if __name__ == "__main__":
    # Third plot (Transmission Plot) - Top Right with Inset
    import generate_transmission_plots as gte
    experiment_id = '413b3b49-c536-427f-a0fd-f0859052f0bd'  # Set the experiment ID
    engine = gte.__get_engine('../data/overweekend_loop_phase_search')  # Ensure correct database name and engine creation
    power_grid, voltages, frequencies, settings = gte.__get_data_from_db(engine, experiment_id)

    fig, ax_main = plt.subplots(figsize=(10, 6))
    generate(ax_main, power_grid, voltages, frequencies)
    plt.tight_layout()
    plt.show()
