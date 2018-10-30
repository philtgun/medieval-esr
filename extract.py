import csv
import numpy as np
import pandas as pd
import itertools as it
import venn
import matplotlib.pyplot as plt


default_infile = 'data/tracks_tags.csv'
default_outfile = 'results/stats.csv'
accepted_types = {
    # 'genre',
    # 'audiodescriptor',
    # 'uncategorized',
    # 'instrument',
    'vartags'
}
accepted_sources = {
    'team',
    'artist',
    # 'bmat',
    # 'mturk'
    # 'auto1',
    # 'auto2',
}


def read_data(filename=default_infile):
    tags_map = {}
    track_ids = set()
    df = pd.read_csv(filename)
    for row in df.itertuples():
        if row.type in accepted_types and row.source in accepted_sources:
            track_ids.add(row.trackId)
            if row.value not in tags_map:
                tags_map[row.value] = set()
            tags_map[row.value].add(row.trackId)

    return tags_map, len(track_ids)


def get_top_tags(tags_map):
    df = pd.DataFrame()
    df['Tag'] = list(tags_map.keys())
    df['Count'] = [len(vals) for vals in tags_map.values()]
    df = df.sort_values(by=['Count'], ascending=False)
    df = df.reset_index(drop=True)
    return df


def print_tags(tags_map):
    for tag_value, track_ids in tags_map.items():
        print('{}: {}'.format(tag_value, len(track_ids)))


if __name__ == '__main__':
    data, total = read_data()
    out_df = get_top_tags(data)
    out_df.to_csv(default_outfile)

