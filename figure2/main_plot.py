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

    # Generate each frame and place it in the appropriate subplot
    ax1 = fig.add_subplot(gs[0, 0])
    generate_frame_NR_Theory(ax1)
    # ax1.text(-0.1, 1.1, 'a', transform=ax1.transAxes, fontsize=16, fontweight='bold', va='top', ha='right')

    ax3 = fig.add_subplot(gs[1, 0])
    generate_frame_NR_Data(ax3)
    # ax3.text(-0.1, 1.1, 'b', transform=ax3.transAxes, fontsize=16, fontweight='bold', va='top', ha='right')

    ax2 = fig.add_subplot(gs[0, 1])
    generate_frame_PT_Theory(ax2)
    # ax2.text(-0.1, 1.1, 'c', transform=ax2.transAxes, fontsize=16, fontweight='bold', va='top', ha='right')

    ax4 = fig.add_subplot(gs[1, 1])
    generate_frame_PT_Data(ax4)
    # ax4.text(-0.1, 1.1, 'd', transform=ax4.transAxes, fontsize=16, fontweight='bold', va='top', ha='right')

    plt.tight_layout(pad=3.0)
    plt.savefig('figure2.png', dpi=SAVE_DPI)
    plt.show()


if __name__ == "__main__":
    main()
