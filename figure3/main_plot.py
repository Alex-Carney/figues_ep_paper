import matplotlib.pyplot as plt
from figure3.config import SAVE_DPI
from frame_one_derivative import generate as generate_frame_one_derivative
from frame_colorplot import generate as generate_frame_colorplot
import generate_transmission_plots as gte


def plot_colorplot_only(power_grid, voltages, frequencies):
    fig, ax = plt.subplots(figsize=(16, 8))
    generate_frame_colorplot(ax, power_grid, voltages, frequencies)
    plt.tight_layout()
    plt.savefig('figure_colorplot_only.png', dpi=SAVE_DPI)
    plt.show()


def plot_side_by_side(power_grid, voltages, frequencies):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    generate_frame_colorplot(ax1, power_grid, voltages, frequencies)
    generate_frame_one_derivative(ax2, power_grid, voltages, frequencies)
    plt.tight_layout()
    plt.savefig('figure_side_by_side.png', dpi=SAVE_DPI)
    plt.show()


def main():
    # Set the experiment ID and load data
    experiment_id = '413b3b49-c536-427f-a0fd-f0859052f0bd'
    engine = gte.__get_engine('../data/overweekend_loop_phase_search')
    power_grid, voltages, frequencies, settings = gte.__get_data_from_db(engine, experiment_id)

    # Plot the color plot only
    plot_colorplot_only(power_grid, voltages, frequencies)

    # Plot side-by-side color plot and derivative plot
    plot_side_by_side(power_grid, voltages, frequencies)


if __name__ == "__main__":
    main()
