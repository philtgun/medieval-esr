import argparse
import pandas as pd

TYPES = [
    'vartags',
    'genre',
    'audiodescriptor',
    'uncategorized',
    'instrument',
]

SOURCES = {
    'team',
    'artist',
    'bmat',
    'mturk'
    'auto1',
    'auto2',
}


def get_tags_dict(filename, types, sources):
    """Returns dictionary that maps tag to set of track_ids, i.e. {'tag': {1,2,3}} and total number of tracks"""
    tags_dict = {}  # dictionary to return
    track_ids = set()  # set of all track_ids
    df = pd.read_csv(filename)
    for row in df.itertuples():
        if row.type in types and row.source in sources:
            track_ids.add(row.trackId)

            if row.value not in tags_dict:
                tags_dict[row.value] = set()
            tags_dict[row.value].add(row.trackId)

    return tags_dict, len(track_ids)


def get_top_tags(tags_dict):
    """Takes dictionary, orders keys according to the length of values, and returns dataframe: tag, len(value)"""
    df = pd.DataFrame()
    df['tag'] = list(tags_dict.keys())
    df['count'] = [len(vals) for vals in tags_dict.values()]
    df = df.sort_values(by=['count'], ascending=False)
    df = df.reset_index(drop=True)
    return df


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Computes the top tags from Jamendo metadata.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-i', '--input', default='data/tracks_tags.csv',
                        help='Input CSV file that is formatted like this: trackId, type, value, source')
    parser.add_argument('-o', '--output', default='results/stats.csv',
                        help='Output CSV file that is formatted like this: rank, tag, count')
    parser.add_argument('-t', '--types', nargs='+', choices=TYPES, default=['vartags'],
                        help='Types of metadata that are processed')
    parser.add_argument('-s', '--sources', nargs='+', choices=SOURCES, default=['team', 'artist'],
                        help='Types of metadata that are considered')
    args = parser.parse_args()

    data, total = get_tags_dict(args.input, args.types, args.sources)
    result = get_top_tags(data)
    result.to_csv(args.output)
    print("Extracted {} tags".format(len(result)))
