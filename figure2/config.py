# config.py
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

LABEL_FONT_SIZE = 23
INSET_LABEL_FONT_SIZE = 15
TICK_FONT_SIZE = 20
INSET_TICK_FONT_SIZE = 16
SAVE_DPI = 400

LEGEND_FONT_SIZE = 16

NUM_Y_TICKS = 7
NUM_X_TICKS = 5

# Colors
FREQ_LINE_COLOR = 'royalblue'
EP_LINE_COLOR = 'lime'

# Cutoff voltages
CUTOFF_VOLTAGES = {
    '3.50 dB': 0.195,
    '4.00 dB': 0.242,
    '4.75 dB': 0.285,
    '5.50 dB': 0.352
}

VOLTS_TO_MUT = 1428.6

VEC_B = r'$\vec{B}$'


# Other configurations as needed


def set_y_ticks(ax, reverse=False):
    y_min, y_max = ax.get_ylim()
    y_ticks = np.linspace(y_min, y_max, NUM_Y_TICKS)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([f"{tick:.3f}" for tick in (y_ticks[::-1] if reverse else y_ticks)])


def set_x_ticks(ax, num_dec, reverse=False):
    x_min, x_max = ax.get_xlim()
    x_ticks = np.linspace(x_min, x_max, NUM_X_TICKS)
    ax.set_xticks(x_ticks)
    # Dynamically create the format string based on num_dec
    format_str = f"{{:.{num_dec}f}}"  # e.g., "{:.3f}" for 3 decimals
    ax.set_xticklabels([format_str.format(tick) for tick in (x_ticks[::-1] if reverse else x_ticks)])
