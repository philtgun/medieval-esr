import argparse
import pandas as pd


def scale_convert(x):
    """Transforms from 1:9 scale to -1:1"""
    return ((x - 1) / 8 - 0.5) * 2


def get_quadrant(valence, arousal):
    """Transforms (arousal, valence) pair to quadrant id"""
    if valence > 0 and arousal > 0:
        return 1
    if valence < 0 < arousal:
        return 2
    if valence < 0 and arousal < 0:
        return 3
    return 4


def get_df_value(df, name):
    """Read name.Mean.Sum from dataframe and convert to -1:1 scale"""
    return scale_convert(df.iloc[0][name + '.Mean.Sum'])


def intersect(tags_filename, emotion_filename):
    """Reads data from tags file, intersects and and augments it with emotion data"""
    emotion_df = pd.read_csv(emotion_filename)
    tags_df = pd.read_csv(tags_filename)
    result_df = pd.DataFrame(columns=['tag', 'count', 'valence', 'arousal', 'quadrant'])

    print('Input tags: {}'.format(len(tags_df)))
    for row in tags_df.itertuples():
        words_df = emotion_df[emotion_df.Word == row.tag]
        if len(words_df) > 0:
            valence = get_df_value(words_df, 'V')
            arousal = get_df_value(words_df, 'A')
            result_df = result_df.append({
                'tag': row.tag,
                'count': row.count,
                'valence': valence,
                'arousal': arousal,
                'quadrant': get_quadrant(valence, arousal)
            }, ignore_index=True)

    print('Output tags: {}'.format(len(result_df)))
    return result_df


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Intersects the top Jamendo tags with Warriner\'s list, adds '
                                                 'arousal-valence values and quadrant',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-i', '--input', default='results/stats.csv',
                        help='Input CSV file with top Jamendo tags (rank, tag, count)')
    parser.add_argument('-e', '--emotion', default='data/BRM-emot-submit.csv',
                        help='Input CSV file with word emotion values (Word, V.Mean.Sum, A.Mean.Sum)')
    parser.add_argument('-o', '--output', default='results/stats_intersected.csv',
                        help='Output CSV file (rank, tag, count, valence, arousal, quadrant)')
    args = parser.parse_args()

    result = intersect(args.input, args.emotion)
    result.to_csv(args.output, float_format='%.2f')
