# frame_C.py
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.colors import Normalize
from config import LABEL_FONT_SIZE, TICK_FONT_SIZE, INSET_TICK_FONT_SIZE, \
    INSET_LABEL_FONT_SIZE, LEGEND_FONT_SIZE, set_y_ticks  # Assuming these are shared settings

# Load data
ced = pd.read_csv('../data/combined_freq_splitting.csv')
all_peaks_df = pd.read_csv('../data/combined_peak_positions.csv')

# Constants
FREQ_LINE_COLOR = 'royalblue'
colors = {
    '3.50 dB': 'forestgreen',
    '4.00 dB': 'royalblue',
    '4.75 dB': '#483D8B',  # Deep purple
    '5.50 dB': 'crimson'
}
cutoff_voltages = {
    '3.50 dB': 0.195,
    '4.00 dB': 0.242,
    '4.75 dB': 0.285,
    '5.50 dB': 0.352
}
labels = ['3.50 dB', '4.00 dB', '4.75 dB', '5.50 dB']
expr_ids = [
    'd2f8d3ef-058f-4b24-b29c-adbfacc0a945',
    '413b3b49-c536-427f-a0fd-f0859052f0bd',
    'f8c20231-bf62-4eb3-aa7d-f7b14c24b023',
    'dd9a4349-7bfa-4500-9b95-117299cf0d1f'
]

def generate(ax_main):
    # Main plot (Peak Locations vs. Voltage)
    grouped = all_peaks_df.groupby('label')
    for label, group in grouped:
        normalized_label = label.replace('Experiment', '').strip()
        cutoff_voltage = cutoff_voltages.get(normalized_label + ' dB')
        if cutoff_voltage:
            filtered_group = group[group['voltage'] <= cutoff_voltage]  # Filter data below cutoff
            ax_main.scatter(
                filtered_group['voltage'],
                filtered_group['peak_freq'] / 1e9,
                label=f'Γ = {normalized_label}',
                color=colors[normalized_label + ' dB']
            )

    ax_main.set_ylabel('Readout Frequency [GHz]', fontsize=LABEL_FONT_SIZE)
    ax_main.tick_params(axis='both', labelsize=TICK_FONT_SIZE)
    ax_main.legend(loc='lower left', fontsize=LEGEND_FONT_SIZE, fancybox=True, framealpha=1)

    # Create inset plot for Frequency Splitting vs. Voltage
    ax_inset = inset_axes(ax_main, width="35%", height="35%", loc="upper right")
    for label, expr_id in zip(labels, expr_ids):
        subset = ced[ced['experiment_id'] == expr_id]
        cutoff_voltage = cutoff_voltages.get(label)
        if cutoff_voltage:
            filtered_subset = subset[subset['voltage'] <= cutoff_voltage]  # Filter data below cutoff
            ax_inset.scatter(
                filtered_subset['voltage'],
                filtered_subset['freq_diff'] / 1e6,
                label=f'Γ = {label}',
                color=colors[label]
            )

    ax_inset.set_ylabel('Splitting (MHz.)', fontsize=INSET_LABEL_FONT_SIZE)
    ax_inset.tick_params(axis='both', labelsize=INSET_TICK_FONT_SIZE)

    ax_main.set_ylim([5.997, 6.036])
    ax_main.set_xlabel('Voltage (V)', fontsize=LABEL_FONT_SIZE)

    set_y_ticks(ax_main)

    return ax_main

# Driver code for standalone testing
if __name__ == "__main__":
    fig, ax_main = plt.subplots(figsize=(10, 6))
    generate(ax_main)
    plt.tight_layout()
    plt.show()