import shared.generate_transmission_plots as gte
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from figure1.config import FIG1_LABEL_FONT_SIZE, FIG1_TICK_FONT_SIZE
from shared.constants import VOLTS_TO_MUT, VEC_B


def generate_frame(ax, engine, experiment_id, title, add_x_label=False, add_y_label=False):
    try:
        # Query the data for the experiment
        power_grid, voltages, frequencies, settings = gte.__get_data_from_db(engine, experiment_id)

        print(f"  Voltages shape: {voltages.shape}")

        # Check if the data is empty
        if power_grid is None:
            return

        # Plot the data on the provided axes
        c = ax.pcolormesh(voltages * VOLTS_TO_MUT, frequencies / 1e9, power_grid.T, shading='auto', cmap='inferno', vmin=-40, vmax=8)
        ax.set_title(title, fontsize=FIG1_LABEL_FONT_SIZE)  # Set the custom title

        # Add X label only if specified
        if add_x_label:
            ax.set_xlabel('$\Delta$' + VEC_B + '[$\mu$T]', fontsize=FIG1_LABEL_FONT_SIZE)

        # Add Y label only if specified
        if add_y_label:
            ax.set_ylabel('Frequency [GHz]', fontsize=FIG1_LABEL_FONT_SIZE)

        ax.tick_params(axis='both', which='major', labelsize=FIG1_TICK_FONT_SIZE)

        ax.set_xlim([.2 * VOLTS_TO_MUT, .7 * VOLTS_TO_MUT])
        ax.set_ylim([5.990, 6.015])

    except Exception as e:
        # Gracefully handle errors for individual experiments
        ax.set_title("Failed", fontsize=10, color='red')
        print(f"Error with experiment {experiment_id}: {e}")


def main():
    # List of experiment IDs
    experiment_ids = [
        "00fefd3f-9a67-4b47-ab8c-d223671244cb",
        "8ab6d7df-2082-4ade-9a80-ca007f723a61",
        "280e8ad4-eea1-43ed-8a3e-01606d330742",
        "81486bdf-27bd-4d2b-9c91-d3c44502df27",
        "e288e062-4639-479a-8571-08c404a45d15",
        "aa0af2fa-4ce0-4573-a30e-796d2461a9d7"  # Last experiment exists in a different database
    ]

    # Titles for the plots
    phi_labels = ["0", "$\pi$"]
    gamma_labels = [25, 20, 15]

    # Create the grid spec with 3 rows and 2 columns
    fig = plt.figure(figsize=(12, 10))  # Adjust the size as needed
    gs = GridSpec(3, 2, figure=fig)

    # Loop through the experiment IDs and plot them
    for idx, experiment_id in enumerate(experiment_ids):
        row, col = divmod(idx, 2)  # Determine row and column index in the grid
        ax = fig.add_subplot(gs[row, col])  # Get the appropriate subplot

        # Determine label conditions
        add_y_label = (col == 0)  # Y label only for plots on the left
        add_x_label = (row == 2)  # X label only for plots on the bottom

        # Determine the title
        phi_label = phi_labels[col]  # Phi depends on the column
        gamma_label = gamma_labels[row]  # Gamma depends on the row
        title = f"$\phi$ = {phi_label}, $\Gamma$ = {gamma_label}"

        # Use a different database for the last experiment
        if idx == len(experiment_ids) - 1:  # Last experiment
            engine = gte.__get_engine('../data/thursday_overmorning')
        else:
            engine = gte.__get_engine('../data/wednesday_overnight')

        # Generate the frame with the custom title
        generate_frame(ax, engine, experiment_id, title, add_x_label=add_x_label, add_y_label=add_y_label)

    plt.tight_layout()
    plt.savefig('figure1.png', dpi=300)


if __name__ == "__main__":
    main()
