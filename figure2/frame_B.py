# frame_B.py
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from theory import dimer_model_symbolics as sm  # Adjust this based on your project structure
from config import LABEL_FONT_SIZE, TICK_FONT_SIZE, \
    LEGEND_FONT_SIZE, INSET_TICK_FONT_SIZE, INSET_LABEL_FONT_SIZE, \
    NUM_Y_TICKS, set_y_ticks, set_x_ticks  # Assuming you have a config file for shared settings


def generate(ax_main, ax_theory=None, ax_theory_inset=None):
    # Define constants
    J_vals = [0.075, 0.08, 0.085, 0.09]
    lo_freqs = np.linspace(5.6, 6.4, 1000)
    gamma_y_vals = np.linspace(0.15, 0.3, 1000)  # PT parameter sweep
    colors = ['green', 'b', 'purple', 'r']

    # Main plot logic for each J value
    for idx, J_val in enumerate(J_vals):
        symbols_dict = sm.setup_symbolic_equations()
        params = sm.ModelParams(
            J_val=J_val,
            g_val=0.025 - 0.04,
            cavity_freq=6.0,
            w_y=6.0,
            gamma_vec=np.array([0.04, 0.04]),
            drive_vector=np.array([1, 0]),
            readout_vector=np.array([1, 0]),
            phi_val=0,
        )

        # Compute photon numbers
        ss_response_PT = sm.get_steady_state_response_PT(symbols_dict, params)
        photon_numbers_PT = sm.compute_photon_numbers_PT(ss_response_PT, gamma_y_vals, lo_freqs)

        # Initialize lists for peaks and splittings
        peak_gamma_y, peak_lo_freqs, peak_photon_numbers = [], [], []
        splitting_gamma_y_vals, peak_splittings = [], []
        found_single_peak = False
        single_peak_location = None

        # Find peaks for main plot and split tracking
        for i, gam in enumerate(gamma_y_vals):
            photon_numbers_slice = photon_numbers_PT[i, :]
            peaks, _ = find_peaks(photon_numbers_slice, height=np.max(photon_numbers_slice) * 0.1)
            peak_lo = lo_freqs[peaks]
            peak_photons = photon_numbers_slice[peaks]

            if len(peaks) == 1 and not found_single_peak:
                found_single_peak = True
                single_peak_location = gam
            if len(peaks) == 2:
                splitting = abs(peak_lo[1] - peak_lo[0])
                splitting_gamma_y_vals.append(gam)
                peak_splittings.append(splitting)

            peak_gamma_y.extend([gam] * len(peaks))
            peak_lo_freqs.extend(peak_lo)
            peak_photon_numbers.extend(peak_photons)

        # Filter data up to the single peak location for the main plot
        if single_peak_location is not None:
            peak_gamma_y_left_of_single_peak = np.array(peak_gamma_y)
            peak_gamma_y_left_of_single_peak[peak_gamma_y_left_of_single_peak > single_peak_location] = np.nan
            valid_indices = ~np.isnan(peak_gamma_y_left_of_single_peak)
            filtered_peak_gamma_y = peak_gamma_y_left_of_single_peak[valid_indices]
            filtered_peak_lo_freqs = np.array(peak_lo_freqs)[valid_indices]
            filtered_peak_photon_numbers = np.array(peak_photon_numbers)[valid_indices]
        else:
            filtered_peak_gamma_y = np.array(peak_gamma_y)
            filtered_peak_lo_freqs = np.array(peak_lo_freqs)
            filtered_peak_photon_numbers = np.array(peak_photon_numbers)

        # Plot the filtered data on the main plot
        ax_main.scatter(
            filtered_peak_gamma_y,
            filtered_peak_lo_freqs,
            cmap='viridis',
            s=20,
            color=colors[idx],
            label=f'J = {J_val:.2f}'
        )

    # Configure main plot labels and axes
    ax_main.set_xlabel(r'$\gamma_y$ (arb.)', fontsize=LABEL_FONT_SIZE)
    # ax_main.set_ylabel('Frequency (arb.)', fontsize=LABEL_FONT_SIZE)
    ax_main.invert_xaxis()
    ax_main.legend(loc="upper right", fontsize=LEGEND_FONT_SIZE)
    ax_main.tick_params(axis='both', labelsize=TICK_FONT_SIZE)

    # Create an inset for peak splitting, positioned top-left but adjusted to the right
    ax_inset = inset_axes(ax_main, width="35%", height="35%", loc="upper left",
                          bbox_to_anchor=(.01, 0, 1, 1),
                          bbox_transform=ax_main.transAxes)
    ax_inset.invert_xaxis()

    # Plot peak splitting data on the inset
    for idx, J_val in enumerate(J_vals):
        symbols_dict = sm.setup_symbolic_equations()
        params = sm.ModelParams(
            J_val=J_val,
            g_val=0.025 - 0.04,
            cavity_freq=6.0,
            w_y=6.0,
            gamma_vec=np.array([0.04, 0.04]),
            drive_vector=np.array([1, 0]),
            readout_vector=np.array([1, 0]),
            phi_val=0,
        )

        # Recompute photon numbers for inset plot
        ss_response_PT = sm.get_steady_state_response_PT(symbols_dict, params)
        photon_numbers_PT = sm.compute_photon_numbers_PT(ss_response_PT, gamma_y_vals, lo_freqs)

        splitting_gamma_y_vals, peak_splittings = [], []
        found_single_peak = False
        single_peak_location = None

        # Track peak splitting for each gamma_y
        for i, gam in enumerate(gamma_y_vals):
            photon_numbers_slice = photon_numbers_PT[i, :]
            peaks, _ = find_peaks(photon_numbers_slice, height=np.max(photon_numbers_slice) * 0.1)
            peak_lo = lo_freqs[peaks]

            if len(peaks) == 1 and not found_single_peak:
                found_single_peak = True
                single_peak_location = gam

            if len(peaks) == 2:
                splitting = abs(peak_lo[1] - peak_lo[0])
                splitting_gamma_y_vals.append(gam)
                peak_splittings.append(splitting)

        # Filter splitting data for the inset plot
        if single_peak_location is not None:
            splitting_gamma_y_left = np.array(splitting_gamma_y_vals)[
                np.array(splitting_gamma_y_vals) <= single_peak_location]
            peak_splittings_left = np.array(peak_splittings)[np.array(splitting_gamma_y_vals) <= single_peak_location]
        else:
            splitting_gamma_y_left = np.array(splitting_gamma_y_vals)
            peak_splittings_left = np.array(peak_splittings)

        # Plot each trace on the inset
        ax_inset.scatter(
            splitting_gamma_y_left,
            peak_splittings_left,
            color=colors[idx],
            s=20,
            label=f'J = {J_val:.2f}'
        )

    # Configure inset labels and axes
    # ax_inset.set_xlabel(r'$\gamma_y$', fontsize=TICK_FONT_SIZE - 4)
    ax_inset.set_ylabel('Splitting (arb.)', fontsize=INSET_LABEL_FONT_SIZE)
    ax_inset.yaxis.set_label_position("right")
    ax_inset.yaxis.tick_right()
    ax_inset.tick_params(axis='both', labelsize=INSET_TICK_FONT_SIZE)
    ax_inset.set_xlim([.31, .16])

    # Set y-axis limits for the main plot
    ax_main.set_ylim([5.9, 6.19])

    # ax_main.set_ylim([5.994, 6.009])
    ax_main.set_xlim(.295, .15)

    set_y_ticks(ax_main)

    ax_main.set_xticks([])
    ax_main.set_xlabel('')

    if ax_theory:
        # ax_main.set_xticks(ax_main.get_xticks())  # Keep the positions
        # ax_main.set_xticklabels(ax_theory.get_xticks())  # Use the source's tick labels

        ax_main.set_yticks(ax_main.get_yticks())  # Keep the positions
        ax_main.set_yticklabels([f"{tick:.3f}" for tick in ax_theory.get_yticks()])

    if ax_theory_inset:
        # set all ticks to nothing
        ax_inset.set_xticks([])
        ax_inset.set_yticks([])
        ax_inset.set_ylabel('')

    return ax_main


# Driver code for standalone testing
if __name__ == "__main__":
    fig, ax_main = plt.subplots(figsize=(10, 6))
    generate(ax_main)
    plt.tight_layout()
    plt.show()
