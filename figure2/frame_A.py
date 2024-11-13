# frame_A.py
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from theory import dimer_model_symbolics as sm  # Adjust this based on your project structure
from config import LABEL_FONT_SIZE, TICK_FONT_SIZE, INSET_TICK_FONT_SIZE, LEGEND_FONT_SIZE, \
    INSET_LABEL_FONT_SIZE  # Assuming a config file for shared settings


def generate(ax_main):
    # Define constants
    J_vals = [0.06, 0.07, 0.08, 0.09]
    lo_freqs = np.linspace(5.6, 6.4, 1000)  # LO frequencies
    yig_freqs = np.linspace(5.6, 5.9, 1000)  # YIG frequencies
    colors = ['r', 'purple', 'b', 'green']

    # Create inset plot
    ax_inset = inset_axes(ax_main, width="35%", height="35%", loc="upper right")

    # Main and inset plot logic
    for idx, J_val in enumerate(J_vals):
        # Set up symbolic parameters
        symbols_dict = sm.setup_symbolic_equations()
        params = sm.ModelParams(
            J_val=J_val,
            g_val=0.025 - 0.04,
            cavity_freq=6.0,
            w_y=6.0,
            gamma_vec=np.array([0.025, 0.025]),
            drive_vector=np.array([1, 1]),
            readout_vector=np.array([1, 1]),
            phi_val=np.pi,
        )

        # Compute photon numbers
        ss_response_NR = sm.get_steady_state_response_NR(symbols_dict, params)
        photon_numbers_NR = sm.compute_photon_numbers_NR(ss_response_NR, yig_freqs, lo_freqs)

        # Initialize lists for peaks and splittings
        peak_yig_freqs, peak_lo_freqs, peak_photon_numbers = [], [], []
        splitting_yig_freqs, peak_splittings = [], []
        found_single_peak, single_peak_location = False, None

        # Find peaks for the main plot and track split data
        for i, yig in enumerate(yig_freqs):
            photon_numbers_slice = photon_numbers_NR[i, :]
            peaks, _ = find_peaks(photon_numbers_slice, height=np.max(photon_numbers_slice) * 0.1)
            peak_lo = lo_freqs[peaks]
            peak_photons = photon_numbers_slice[peaks]

            if len(peaks) == 1 and not found_single_peak:
                found_single_peak = True
                single_peak_location = yig
            if len(peaks) == 2:
                splitting = abs(peak_lo[1] - peak_lo[0])
                splitting_yig_freqs.append(yig)
                peak_splittings.append(splitting)

            peak_yig_freqs.extend([yig] * len(peaks))
            peak_lo_freqs.extend(peak_lo)
            peak_photon_numbers.extend(peak_photons)

        # Filter main plot data up to the single peak location
        if single_peak_location is not None:
            peak_yig_freqs_left = np.array(peak_yig_freqs)
            peak_yig_freqs_left[peak_yig_freqs_left > single_peak_location] = np.nan
            valid_indices = ~np.isnan(peak_yig_freqs_left)
            filtered_peak_yig_freqs = peak_yig_freqs_left[valid_indices]
            filtered_peak_lo_freqs = np.array(peak_lo_freqs)[valid_indices]
            filtered_peak_photon_numbers = np.array(peak_photon_numbers)[valid_indices]
        else:
            filtered_peak_yig_freqs = np.array(peak_yig_freqs)
            filtered_peak_lo_freqs = np.array(peak_lo_freqs)
            filtered_peak_photon_numbers = np.array(peak_photon_numbers)

        # Plot the filtered data on the main plot
        ax_main.scatter(
            filtered_peak_yig_freqs,
            filtered_peak_lo_freqs,
            cmap='viridis',
            s=20,
            color=colors[idx],
            label=f'J = {J_val:.2f}'
        )

        # Filter and plot peak splitting data on the inset
        splitting_yig_freqs_left = np.array(splitting_yig_freqs)[np.array(splitting_yig_freqs) <= single_peak_location]
        peak_splittings_left = np.array(peak_splittings)[np.array(splitting_yig_freqs) <= single_peak_location]
        ax_inset.scatter(
            splitting_yig_freqs_left,
            peak_splittings_left,
            color=colors[idx],
            s=20,
            label=f'J = {J_val:.2f}'
        )

    # Configure main plot labels and legend
    ax_main.set_xlabel(r'$\omega_{YIG}$ (arb.)', fontsize=LABEL_FONT_SIZE)
    ax_main.set_ylabel('Frequency (arb.)', fontsize=LABEL_FONT_SIZE)
    ax_main.invert_yaxis()
    ax_main.legend(loc="lower left", fontsize=LEGEND_FONT_SIZE, fancybox=True, framealpha=1)
    ax_main.tick_params(axis='both', labelsize=TICK_FONT_SIZE)

    ax_main.set_ylim([6.02, 5.58])

    # Increase number of Y ticks
    ax_main.yaxis.set_major_locator(plt.MaxNLocator(7))

    # Get the current y-tick positions
    y_ticks = ax_main.get_yticks()
    ax_main.set_yticks(y_ticks)
    ax_main.set_yticklabels([f"{tick:.3f}" for tick in y_ticks[::-1]])


    # Configure inset labels and legend
    # ax_inset.set_xlabel('YIG Frequency (GHz)', fontsize=INSET_TICK_FONT_SIZE)

    # ax_inset.legend(fontsize=INSET_TICK_FONT_SIZE)
    ax_inset.set_ylabel('Splitting (arb.)', fontsize=INSET_LABEL_FONT_SIZE)
    ax_inset.tick_params(axis='both', labelsize=INSET_TICK_FONT_SIZE)

    return ax_main

# Driver code for standalone testing
if __name__ == "__main__":
    fig, ax_main = plt.subplots(figsize=(10, 6))
    generate(ax_main)
    plt.tight_layout()
    plt.show()