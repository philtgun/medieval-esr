import argparse
import pandas as pd
import matplotlib.pyplot as plt


def plot_quadrants(input_filename, output_filename, n, labels, show):
    """Plots tags on arousal-valence space"""
    df = pd.read_csv(input_filename)

    if n is not None:
        df = df[:n]

    plt.scatter(df.valence, df.arousal, df['count'].astype(float) / 15, alpha=0.7)

    if labels:
        for i, tag in enumerate(df.tag):
            plt.text(df.valence.iloc[i] - 0.05, df.arousal.iloc[i], tag, fontsize=8)

    plt.ylim([-1, 1])
    plt.xlim([-1, 1])
    plt.hlines(0, -1, 1, linestyles=':')
    plt.vlines(0, -1, 1, linestyles=':')
    plt.xlabel('Valence')
    plt.ylabel('Arousal')
    plt.title('Distribution of tags' + (' (top {})'.format(n) if n else ''))
    plt.savefig(output_filename)

    if show:
        plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plots tags on arousal-valence space',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-i', '--input', default='results/stats_intersected.csv',
                        help='Input CSV file (rank, tag, count, valence, arousal, quadrant)')
    parser.add_argument('-o', '--output', default='results/distribution.png',
                        help='Figure file with tags plotted on arousal-valence space')
    parser.add_argument('-s', '--show', action='store_true', default=False, help='Show figure in the end')
    parser.add_argument('-n', '--num', type=int, default=None, help='Number of tags to display')
    parser.add_argument('-l', '--labels', action='store_false', default=True, help='Hide labels')
    args = parser.parse_args()

    plot_quadrants(args.input, args.output, args.num, args.labels, args.show)
