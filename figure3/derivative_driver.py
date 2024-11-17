import matplotlib.pyplot as plt
from matplotlib import gridspec

from frame_one_derivative import generate as generate_frame_one_derivative
from frame_upper_branch_derivative import generate as generate_frame_upper_branch_derivative

from shared import generate_transmission_plots as gte


def main():
    experiment_id = '413b3b49-c536-427f-a0fd-f0859052f0bd'
    engine = gte.__get_engine('../data/overweekend_loop_phase_search')
    power_grid, voltages, frequencies, settings = gte.__get_data_from_db(engine, experiment_id)

    fig = plt.figure(figsize=(20, 8))
    gs = gridspec.GridSpec(1, 2)

    ax1 = fig.add_subplot(gs[0, 0])
    ax1_main, ax1_dual = generate_frame_one_derivative(ax1, power_grid, voltages, frequencies, True)

    ax2 = fig.add_subplot(gs[0, 1])
    generate_frame_upper_branch_derivative(ax2, power_grid, voltages, frequencies, ax1_main, ax1_dual, True)


if __name__ == "__main__":
    main()
