import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.colors import Normalize
from matplotlib import cm

# Constants for font sizes and DPI
LABEL_FONT_SIZE = 23
TICK_FONT_SIZE = 20
SAVE_DPI = 400

# PLOT OPTIONS
FREQ_LINE = 6.009e9  # Frequency for the horizontal line (adjust as needed)
VOLTAGE_LINE = 0.254  # Voltage for the vertical line (adjust as needed)
FREQ_LINE_COLOR = 'royalblue'
EP_LINE_COLOR = 'lime'
SHOW_INSET_AXIS_LABELS = False  # Set to True if you want labels on the inset axes

# Load the data (replace 'your_data.csv' with your actual data file)
# Ensure that your data file has the necessary columns: 'voltage', 'frequency', 'power'
data = pd.read_csv('your_data.csv')

# Extract the necessary data
voltages = data['voltage'].values
frequencies = data['frequency'].values
power_grid = data['power'].values.reshape(len(np.unique(voltages)), len(np.unique(frequencies)))

# Create the figure and axis
fig, ax = plt.subplots(figsize=(8, 6))

# Generate the color plot (transmission plot)
pcm = ax.pcolormesh(
    voltages,
    frequencies / 1e9,  # Convert frequencies to GHz if needed
    power_grid.T,
    shading='auto',
    cmap='inferno',  # Adjust colormap as desired
    vmin=-40,        # Adjust the color scale limits as needed
    vmax=8
)

# Add a colorbar
cbar = fig.colorbar(pcm, ax=ax, label='$S_{21}$ [dB]')
cbar.ax.tick_params(labelsize=TICK_FONT_SIZE)

# Set labels and title
ax.set_xlabel('Voltage [V]', fontsize=LABEL_FONT_SIZE)
ax.set_ylabel('Frequency [GHz]', fontsize=LABEL_FONT_SIZE)
ax.tick_params(axis='both', labelsize=TICK_FONT_SIZE)
ax.set_title('Transmission Plot', fontsize=LABEL_FONT_SIZE)

# Add horizontal and vertical lines
ax.axhline(y=FREQ_LINE / 1e9, color=FREQ_LINE_COLOR, linestyle='--', linewidth=3, alpha=0.7)
ax.axvline(x=VOLTAGE_LINE, color=EP_LINE_COLOR, linestyle='--', linewidth=3, alpha=0.7)

# Optionally, overlay peak positions
# If you have a DataFrame 'peaks_df' with 'voltage' and 'peak_freq' columns
peaks_df = pd.read_csv('../data/combined_peak_positions.csv')
ax.scatter(
    peaks_df['voltage'],
    peaks_df['peak_freq'] / 1e9,
    color='white',
    s=50,
    marker='*',
    label='Peak Positions'
)

# Add legend if needed
ax.legend(fontsize=TICK_FONT_SIZE)

# Show or save the plot
plt.tight_layout()
plt.savefig('transmission_plot.png', dpi=SAVE_DPI)
plt.show()
