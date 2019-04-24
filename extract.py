import argparse
import pandas as pd
import json
from os import path

TYPES = [
    'vartags',
    'genre',
    'audiodescriptor',
    'uncategorized',
    'instrument',
]

SOURCES = [
    'team',
    'artist',
    'bmat',
    'mturk'
    'auto1',
    'auto2',
]


def get_tags_tracks(filename, types, sources):
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

    print("Total tracks in input: {}".format(len(track_ids)))
    print("Extracted {} tags".format(len(tags_dict)))
    return tags_dict, track_ids


def get_tags_stats(tags_dict):
    """Takes dictionary, orders keys according to the length of values, and returns dataframe: tag, len(value)"""
    df = pd.DataFrame()
    df['tag'] = list(tags_dict.keys())
    df['count'] = [len(vals) for vals in tags_dict.values()]
    df = df.sort_values(by=['count'], ascending=False)
    df = df.reset_index(drop=True)
    return df


def get_tracks_mapping(filename, track_ids):
    with open(filename) as fp:
        tracks = json.load(fp)

    albums = {}
    artists = {}
    for track in tracks:
        track_id = int(track['id'])
        if track_id in track_ids:
            albums[track_id] = int(track['album_id'])
            artists[track_id] = int(track['artist_id'])

    print("Total tracks in API dump: {}".format(len(tracks)))
    print("Total tracks in both: {}".format(len(albums)))
    print("Total albums with tags: {}".format(len(set(albums.values()))))
    print("Total artists with tags: {}".format(len(set(artists.values()))))
    return albums, artists


def get_tags_to_collections(tags_tracks, collection):
    tags_collections = {}
    for tag, track_ids in tags_tracks.items():
        tags_collections[tag] = set()
        for track_id in track_ids:
            if track_id in collection:
                # to support subsetting track_ids - if collection is set-like, we just intersect
                try:
                    value = collection[track_id]
                except TypeError:
                    value = track_id
                tags_collections[tag].add(value)
    return tags_collections


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Computes the top tags from Jamendo metadata.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-i', '--input', default='data/tracks_tags.csv',
                        help='Input CSV file that is formatted like this: trackId, type, value, source')
    parser.add_argument('-a', '--api-input', default='data/good-jamendo-licensing-2018-02-02.json',
                        help='Input JSON file that is an array of dicts with keys: id, artist_id, album_id')
    parser.add_argument('-d', '--directory', default='results_artist',
                        help='Output directory where the filed will be written (should exist)')
    parser.add_argument('-p', '--prefix', default='stats',
                        help='Output prefix of CSV files')
    parser.add_argument('-t', '--types', nargs='+', choices=TYPES, default=['genre'],
                        help='Types of metadata that are processed')
    parser.add_argument('-s', '--sources', nargs='+', choices=SOURCES, default=['artist'],
                        help='Types of metadata that are considered')
    args = parser.parse_args()

    tags_to_tracks, tracks_all = get_tags_tracks(args.input, args.types, args.sources)
    tracks_to_albums, tracks_to_artists = get_tracks_mapping(args.api_input, tracks_all)
    tags_to_albums = get_tags_to_collections(tags_to_tracks, tracks_to_albums)
    tags_to_artists = get_tags_to_collections(tags_to_tracks, tracks_to_artists)
    tags_to_tracks_subset = get_tags_to_collections(tags_to_tracks, tracks_to_albums.keys())

    get_tags_stats(tags_to_tracks).to_csv(path.join(args.directory, args.prefix + "_tracks_all.csv"))
    get_tags_stats(tags_to_tracks_subset).to_csv(path.join(args.directory, args.prefix + "_tracks.csv"))
    get_tags_stats(tags_to_albums).to_csv(path.join(args.directory, args.prefix + "_albums.csv"))
    get_tags_stats(tags_to_artists).to_csv(path.join(args.directory, args.prefix + "_artists.csv"))
