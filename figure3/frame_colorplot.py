import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib import cm
from shared import generate_transmission_plots as gte
import derivative_plots_with_sqrt_ontop as dgte
from figure3.config import FREQ_LINE, FREQ_LINE_COLOR, EP_LINE_COLOR, VOLTAGE_LINE, INSET_LABEL_FONT_SIZE, VOLTS_TO_MUT, \
 UPPER_BRANCH_FREQ_LINE, UPPER_BRANCH_LINE_COLOR

from matplotlib.path import Path

from shared.constants import VEC_B


def custom_box_style(pad_left, pad_right, pad_bottom, pad_top):
    def box_style(x0, y0, width, height, mutation_size):
        # Calculate new position and size without modifying x0 and y0 in place
        x0_new = x0 - pad_left
        y0_new = y0 - pad_bottom
        width_new = width + pad_left + pad_right
        height_new = height + pad_bottom + pad_top

        # Define the path of the box using the new dimensions
        path = Path([
            (x0_new, y0_new),  # Lower-left corner
            (x0_new + width_new, y0_new),  # Lower-right corner
            (x0_new + width_new, y0_new + height_new),  # Upper-right corner
            (x0_new, y0_new + height_new),  # Upper-left corner
            (x0_new, y0_new),  # Back to lower-left
        ])
        return path

    return box_style


# register

# Constants for font sizes and DPI
LABEL_FONT_SIZE = 23
TICK_FONT_SIZE = 20
SAVE_DPI = 400


def generate(ax_main, power_grid, voltages, frequencies):
    # Process traces and filter peak data
    peaks_df = dgte.__process_all_traces(power_grid, voltages, frequencies)
    filtered_peaks_df = peaks_df[(peaks_df['peak_freq'] > FREQ_LINE) & (peaks_df['voltage'] <= 0.25)]

    # Main transmission plot
    c = ax_main.pcolormesh(voltages * VOLTS_TO_MUT, frequencies / 1e9, power_grid.T, shading='auto', cmap='inferno',
                           vmin=-40, vmax=8)

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
                    label='$f_{EP}$ = 6.009 GHz')
    ax_main.axhline(y=UPPER_BRANCH_FREQ_LINE / 1e9, color=UPPER_BRANCH_LINE_COLOR, linestyle='--', linewidth=3,
                    alpha=0.7,
                    label='$f_{UB}$ = 6.015 GHz')
    ax_main.axvline(x=VOLTAGE_LINE * VOLTS_TO_MUT, color=EP_LINE_COLOR, linestyle='--', linewidth=3, alpha=0.7,
                    label='EP Line')
    ax_main.plot(filtered_peaks_df['voltage'] * VOLTS_TO_MUT, filtered_peaks_df['peak_freq'] / 1e9, color='gray',
                 linestyle='--',
                 linewidth=3, label='Upper Branch (UB)')

    # Inset plot for peak data with color-mapped points
    #                             ( x0, y0, width, height )
    inset_ax = ax_main.inset_axes((0.49, 0.63, 0.5, 0.35))
    norm = Normalize(vmin=-40, vmax=8)
    colors = cm.inferno(norm(filtered_peaks_df['peak_power']))
    inset_ax.scatter(filtered_peaks_df['voltage'], filtered_peaks_df['peak_power'], color=colors, s=10,
                     label=r"Upper Branch $S_{21}^{\rm{max}}$")
    inset_ax.legend(fontsize=LABEL_FONT_SIZE - 2, loc='upper center')

    # # For X-tick labels
    # for tick_label in inset_ax.get_xticklabels():
    #     fontsize = tick_label.get_fontsize()  # Font size in points
    #
    #     # Define individual padding values (adjust as needed)
    #     pad_left = fontsize * 25  # Left padding
    #     pad_right = fontsize * 25  # Right padding
    #     pad_bottom = fontsize * 0.05  # Bottom padding
    #     pad_top = fontsize * 5  # Top padding
    #
    #     tick_label.set_bbox(dict(
    #         facecolor='white',
    #         edgecolor='none',
    #         boxstyle=custom_box_style(pad_left, pad_right, pad_bottom, pad_top)
    #     ))
    #
    # # For Y-tick labels
    # for tick_label in inset_ax.get_yticklabels():
    #     fontsize = tick_label.get_fontsize()
    #
    #     # Define individual padding values (adjust as needed)
    #     pad_left = fontsize * 0.2
    #     pad_right = fontsize * 5
    #     pad_bottom = fontsize * 10
    #     pad_top = fontsize * 10
    #
    #     tick_label.set_bbox(dict(
    #         facecolor='white',
    #         edgecolor='none',
    #         boxstyle=custom_box_style(pad_left, pad_right, pad_bottom, pad_top)
    #     ))

    # Move tick marks inside the plot area
    inset_ax.tick_params(axis='x', which='both', direction='in', pad=-15)
    inset_ax.tick_params(axis='y', which='both', direction='in', pad=-20)

    inset_ax.set_ylabel('$S_{21}$ (dBm)', fontsize=INSET_LABEL_FONT_SIZE,
                        bbox=dict(facecolor='white', edgecolor='white', pad=3))
    inset_ax.set_xlabel('$\Delta$' + VEC_B + '[$\mu$T]', fontsize=INSET_LABEL_FONT_SIZE,
                        bbox=dict(facecolor='white', edgecolor='white', pad=3))

    # Set the x ticks to tick * VOLTS_TO_MUT on the main plot

    ax_main.legend(loc='lower left', fontsize=LABEL_FONT_SIZE, fancybox=True, framealpha=1)


# Driver code for standalone testing
if __name__ == "__main__":
    experiment_id = '413b3b49-c536-427f-a0fd-f0859052f0bd'
    engine = gte.__get_engine('../data/overweekend_loop_phase_search')
    power_grid, voltages, frequencies, settings = gte.__get_data_from_db(engine, experiment_id)
    fig, ax_main = plt.subplots(figsize=(20, 8))
    generate(ax_main, power_grid, voltages, frequencies)
    plt.tight_layout()
    plt.savefig('frame_colorplot.png', dpi=SAVE_DPI)
