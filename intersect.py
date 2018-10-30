import pandas as pd
import matplotlib.pyplot as plt

dictionary_filename = 'data/BRM-emot-submit.csv'
default_infile = 'results/stats.csv'
default_outfile = 'results/stats_intersected.csv'


def get_words(filename=dictionary_filename):
    df = pd.read_csv(filename)
    return set(df.Word)


def get_intersection(words, filename=default_infile):
    df = pd.read_csv(filename)
    tags = set(df.Tags)
    common_tags = tags.intersection(words)
    print('{} > {}'.format(len(tags), len(common_tags)))


def scale_convert(x):
    """ Transforms from 1:9 scale to -1:1"""
    return ((x - 1) / 8 - 0.5) * 2


def get_quadrant(valence, arousal):
    if valence > 0 and arousal > 0:
        return 1
    if valence < 0 < arousal:
        return 2
    if valence < 0 and arousal < 0:
        return 3
    return 4


def get_df_value(df, name):
    return scale_convert(df.iloc[0][name + '.Mean.Sum'])


def intersect(dict_filename=dictionary_filename, tags_filename=default_infile):
    dict_df = pd.read_csv(dict_filename)
    tags_df = pd.read_csv(tags_filename)
    out_df = pd.DataFrame(columns=['Tag', 'Count', 'Valence', 'Arousal', 'Quadrant'])

    print('Input tags: {}'.format(len(tags_df)))
    for row in tags_df.itertuples():
        words_df = dict_df[dict_df.Word == row.Tag]

        if len(words_df > 0):
            valence = get_df_value(words_df, 'V')
            arousal = get_df_value(words_df, 'A')
            out_df = out_df.append({
                'Tag': row.Tag,
                'Count': row.Count,
                'Valence': valence,
                'Arousal': arousal,
                'Quadrant': get_quadrant(valence, arousal)
            }, ignore_index=True)

    print('Output tags: {}'.format(len(out_df)))
    return out_df


def plot_quadrants(df, n=None, show=False):
    plt.scatter(df.Valence, df.Arousal, df.Count / 15, alpha=0.7)
    for i, tag in enumerate(df.Tag):
        plt.text(df.Valence.iloc[i] - 0.05, df.Arousal.iloc[i], tag, fontsize=8)

    plt.ylim([-1, 1])
    plt.xlim([-1, 1])
    plt.hlines(0, -1, 1, linestyles=':')
    plt.vlines(0, -1, 1, linestyles=':')
    plt.xlabel('Valence')
    plt.ylabel('Arousal')
    plt.title('Distribution of tags' + ('(top {})'.format(n) if n else ''))
    plt.savefig('results/distribution.png')
    if show:
        plt.show()


if __name__ == '__main__':
    """This script is supposed to be executed after the extraction of tags"""
    df = intersect()
    df.to_csv(default_outfile, float_format='%.2f')
    plot_quadrants(df)

