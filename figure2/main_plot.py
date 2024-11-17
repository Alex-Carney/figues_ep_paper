import matplotlib.pyplot as plt
from matplotlib import gridspec
from config import SAVE_DPI
from frame_A import generate as generate_frame_NR_Theory
from frame_B import generate as generate_frame_PT_Theory
from frame_C import generate as generate_frame_NR_Data
from frame_D import generate as generate_frame_PT_Data


def main():
    # Initialize the figure with GridSpec
    fig = plt.figure(figsize=(16, 12))
    gs = gridspec.GridSpec(2, 2)

    ax4 = fig.add_subplot(gs[1, 1])
    ax4, ax4_inset = generate_frame_PT_Data(ax4)

    ax3 = fig.add_subplot(gs[1, 0])
    ax3, ax3_inset = generate_frame_NR_Data(ax3)

    # Generate each frame and place it in the appropriate subplot
    ax1 = fig.add_subplot(gs[0, 0])
    generate_frame_NR_Theory(ax1, ax3, ax3_inset)
    # generate_frame_NR_Theory(ax1)

    ax2 = fig.add_subplot(gs[0, 1])
    generate_frame_PT_Theory(ax2, ax4, ax4_inset)
    # generate_frame_PT_Theory(ax2)

    plt.tight_layout(pad=3.0)
    plt.savefig('figure2.png', dpi=SAVE_DPI)
    plt.show()


if __name__ == "__main__":
    # Set Helvetica as the default font
    # plt.rcParams['font.family'] = 'Helvetica'
    main()

