import numpy as np
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
from figure3.config import LABEL_FONT_SIZE, TICK_FONT_SIZE, LEGEND_FONT_SIZE

# Define parameters
freq_min = 5.996e9
freq_max = 6.04e9
voltage_min = -0.2
voltage_max = 0.25

def generate(ax_main, power_grid, voltages, frequencies):
    # Create an empty list to store maximum derivatives
    max_derivative_per_frequency = []

    # Filter the frequencies and voltages
    freq_mask = (frequencies >= freq_min) & (frequencies <= freq_max)
    volt_mask = (voltages >= voltage_min) & (voltages <= voltage_max)

    # Apply the masks to filter the data
    filtered_frequencies = frequencies[freq_mask]
    filtered_voltages = voltages[volt_mask]
    filtered_power_grid = power_grid[np.ix_(volt_mask, freq_mask)]

    # Loop over each frequency and compute the derivative of the voltage trace
    for freq_idx, frequency in enumerate(filtered_frequencies):
        # Slice the voltage trace directly from power_grid for the current frequency
        volt_power = filtered_power_grid[:, freq_idx]

        # Smooth the voltage power trace using a Savitzky-Golay filter
        smoothed_volt_power = savgol_filter(volt_power, window_length=25, polyorder=2)

        # Calculate the derivative of the voltage power trace with respect to voltage
        d_volt_power = np.gradient(smoothed_volt_power, filtered_voltages)

        # Find the maximum of this derivative and store it with the corresponding frequency
        max_derivative = np.max(np.abs(d_volt_power))
        max_derivative_per_frequency.append((frequency, max_derivative))

    # Convert results into separate lists for plotting
    frequencies_list, max_derivatives_list = zip(*max_derivative_per_frequency)

    # Plot the maximum derivative against frequency
    ax_main.plot(frequencies_list, max_derivatives_list, color='crimson', label='Max Derivative')
    ax_main.set_xlabel('Frequency [Hz]', fontsize=LABEL_FONT_SIZE)
    ax_main.set_ylabel('Max Derivative [dB/V]', fontsize=LABEL_FONT_SIZE)

    ax_main.tick_params(axis='x', labelsize=TICK_FONT_SIZE)
    ax_main.tick_params(axis='y', labelsize=TICK_FONT_SIZE)

    ax_main.legend(fontsize=LEGEND_FONT_SIZE)

# Driver code for standalone testing
if __name__ == "__main__":
    # Third plot (Transmission Plot) - Top Right with Inset
    import shared.generate_transmission_plots as gte
    experiment_id = '413b3b49-c536-427f-a0fd-f0859052f0bd'  # Set the experiment ID
    engine = gte.__get_engine('../data/overweekend_loop_phase_search')  # Ensure correct database name and engine creation
    power_grid, voltages, frequencies, settings = gte.__get_data_from_db(engine, experiment_id)

    fig, ax_main = plt.subplots(figsize=(10, 6))
    generate(ax_main, power_grid, voltages, frequencies)
    plt.tight_layout()
    plt.show()