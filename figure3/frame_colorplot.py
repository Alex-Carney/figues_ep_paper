import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.colors import Normalize
from matplotlib import cm
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import generate_transmission_plots as gte
import derivative_plots_with_sqrt_ontop as dgte
from figure3.config import FREQ_LINE, FREQ_LINE_COLOR, EP_LINE_COLOR, VOLTAGE_LINE, INSET_TICK_FONT_SIZE, \
    INSET_LABEL_FONT_SIZE, VOLTS_TO_MUT, VEC_B

# Constants for font sizes and DPI
LABEL_FONT_SIZE = 23
TICK_FONT_SIZE = 20
SAVE_DPI = 400


def generate(ax_main, power_grid, voltages, frequencies):
    # Process traces and filter peak data
    peaks_df = dgte.__process_all_traces(power_grid, voltages, frequencies)
    filtered_peaks_df = peaks_df[(peaks_df['peak_freq'] > FREQ_LINE) & (peaks_df['voltage'] <= 0.25)]

    # Main transmission plot
    c = ax_main.pcolormesh(voltages * VOLTS_TO_MUT, frequencies / 1e9, power_grid.T, shading='auto', cmap='inferno', vmin=-40, vmax=8)

    # Main colorbar placed to the right of the main plot
    cbar = plt.colorbar(c, ax=ax_main, orientation="vertical", pad=0.02, aspect=30)
    cbar.set_label('$S_{21}$ [dB]', fontsize=LABEL_FONT_SIZE + 4)
    cbar.ax.tick_params(labelsize=TICK_FONT_SIZE)

    # Set axis limits and labels for main plot
    ax_main.set_ylim(5.997, 6.033)
    ax_main.set_xlabel('$\Delta$' + VEC_B + '[$\mu$T]', fontsize=LABEL_FONT_SIZE + 4)
    ax_main.set_ylabel('Frequency [GHz]', fontsize=LABEL_FONT_SIZE + 4)
    ax_main.tick_params(axis='x', labelsize=TICK_FONT_SIZE)
    ax_main.tick_params(axis='y', labelsize=TICK_FONT_SIZE)

    # Overlay lines and peaks on main plot
    ax_main.axhline(y=FREQ_LINE / 1e9, color=FREQ_LINE_COLOR, linestyle='--', linewidth=3, alpha=0.7,
                    label='$f_c$ = 6.009 GHz')
    ax_main.axvline(x=VOLTAGE_LINE * VOLTS_TO_MUT, color=EP_LINE_COLOR, linestyle='--', linewidth=3, alpha=0.7, label='EP Line')
    ax_main.plot(filtered_peaks_df['voltage'] * VOLTS_TO_MUT, filtered_peaks_df['peak_freq'] / 1e9, color='gray', linestyle='--',
                 linewidth=3, label='Upper Branch')

    # Inset plot for peak data with color-mapped points
    inset_ax = ax_main.inset_axes((0.42, 0.63, 0.56, 0.35))
    norm = Normalize(vmin=-40, vmax=8)
    colors = cm.inferno(norm(filtered_peaks_df['peak_power']))
    inset_ax.scatter(filtered_peaks_df['voltage'], filtered_peaks_df['peak_power'], color=colors, s=10,
                     label=r"Upper Branch $S_{21}^{\rm{max}}$")
    inset_ax.legend(fontsize=LABEL_FONT_SIZE - 2, loc='upper center')

    # Add bounding boxes to X-tick labels
    for tick_label in inset_ax.get_xticklabels():
        tick_label.set_bbox(dict(facecolor='white', edgecolor='none', pad=3))

    # Add bounding boxes to Y-tick labels
    for tick_label in inset_ax.get_yticklabels():
        tick_label.set_bbox(dict(facecolor='white', edgecolor='none', pad=3))

    inset_ax.set_ylabel('$S_{21}$ (dBm)', fontsize=INSET_LABEL_FONT_SIZE,
                        bbox=dict(facecolor='white', edgecolor='none', pad=3))
    inset_ax.set_xlabel('Voltage (V)', fontsize=INSET_LABEL_FONT_SIZE,
                        bbox=dict(facecolor='white', edgecolor='none', pad=3))

    # Set the x ticks to tick * VOLTS_TO_MUT on the main plot

    ax_main.legend(loc='lower right', fontsize=LABEL_FONT_SIZE, fancybox=True, framealpha=1)


# Driver code for standalone testing
if __name__ == "__main__":
    experiment_id = '413b3b49-c536-427f-a0fd-f0859052f0bd'
    engine = gte.__get_engine('../data/overweekend_loop_phase_search')
    power_grid, voltages, frequencies, settings = gte.__get_data_from_db(engine, experiment_id)
    fig, ax_main = plt.subplots(figsize=(12, 8))
    generate(ax_main, power_grid, voltages, frequencies)
    plt.tight_layout()
    plt.savefig('frame_colorplot.png', dpi=SAVE_DPI)
