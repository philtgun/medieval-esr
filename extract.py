import argparse
import pandas as pd
import csv
import json
from os import path

TYPES = [
    'vartags',
    'genre',
    'audiodescriptor',
    'uncategorized',
    'instrument',
]

TYPE_PREFIXES = {
    'vartags': 'moodsnthemes'
}

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
    tags_to_tracks = {}
    tracks_to_tags = {}
    df = pd.read_csv(filename)
    for row in df.itertuples():
        if row.type in types and row.source in sources:
            if row.trackId not in tracks_to_tags:
                tracks_to_tags[row.trackId] = set()
            tracks_to_tags[row.trackId].add(row.value)

            if row.value not in tags_to_tracks:
                tags_to_tracks[row.value] = set()
            tags_to_tracks[row.value].add(row.trackId)

    print('Total tracks in input: {}'.format(len(tracks_to_tags.keys())))
    print('Extracted {} tags'.format(len(tags_to_tracks)))
    return tags_to_tracks, tracks_to_tags


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

    print('Total tracks in API dump: {}'.format(len(tracks)))
    print('Total tracks in both: {}'.format(len(albums)))
    print('Total albums with tags: {}'.format(len(set(albums.values()))))
    print('Total artists with tags: {}'.format(len(set(artists.values()))))
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


def filter_tags(df, threshold):
    df = df[df['count'] >= threshold]
    return set(df['tag'])


def generate_annotations(annotations, filter_stats, filter_threshold, tracks_to_tags, tracks_to_albums,
                         tracks_to_artists, prefix):
    tags = filter_tags(filter_stats, filter_threshold)

    for track in tracks_to_artists:
        track_tags = tracks_to_tags[track] & tags
        if track_tags:
            tags_string = '\t'.join([prefix + '---' + tag for tag in tracks_to_tags[track] & tags])
            if track not in annotations:
                annotations[track] = {
                    'track_id': track,
                    'artist_id': tracks_to_artists[track],
                    'album_id': tracks_to_albums[track],
                    'path': path.join('{:02}'.format(track % 100), '{}.flac'.format(track)),
                    'tags': tags_string
                }
            else:
                annotations[track]['tags'] += '\t' + tags_string

    return annotations


def annotations_to_df(annotations):
    df = pd.DataFrame(annotations.values(), columns=['track_id', 'artist_id', 'album_id', 'path', 'tags'])
    df.set_index('track_id', drop=True)
    df.sort_index()
    return df


def main(input_csv, api_input, directory, prefix, types, sources, annotations, threshold):
    print("- " + ", ".join(types))
    tags_to_tracks, tracks_all_to_tags = get_tags_tracks(input_csv, types, sources)
    tracks_to_albums, tracks_to_artists = get_tracks_mapping(api_input, tracks_all_to_tags.keys())
    tags_to_albums = get_tags_to_collections(tags_to_tracks, tracks_to_albums)
    tags_to_artists = get_tags_to_collections(tags_to_tracks, tracks_to_artists)
    tags_to_tracks_subset = get_tags_to_collections(tags_to_tracks, tracks_to_albums.keys())

    get_tags_stats(tags_to_tracks).to_csv(path.join(directory, prefix + '_tracks_all.csv'))
    get_tags_stats(tags_to_tracks_subset).to_csv(path.join(directory, prefix + '_tracks.csv'))
    get_tags_stats(tags_to_albums).to_csv(path.join(directory, prefix + '_albums.csv'))
    artists = get_tags_stats(tags_to_artists)
    artists.to_csv(path.join(directory, prefix + '_artists.csv'))

    return generate_annotations(annotations, artists, threshold, tracks_all_to_tags, tracks_to_albums, tracks_to_artists, prefix)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Computes the top tags from Jamendo metadata.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-i', '--input', default='data/tracks_tags.csv',
                        help='Input CSV file that is formatted like this: trackId, type, value, source')
    parser.add_argument('-a', '--api-input', default='data/good-jamendo-licensing-2018-02-02.json',
                        help='Input JSON file that is an array of dicts with keys: id, artist_id, album_id')
    parser.add_argument('-d', '--directory', default='results_artist',
                        help='Output directory where the filed will be written (should exist)')
    parser.add_argument('-p', '--prefix', default='',
                        help='Output prefix of CSV files')
    parser.add_argument('-t', '--types', nargs='+', choices=TYPES, default=['genre', 'vartags', 'instrument'],
                        help='Types of metadata that are processed')
    parser.add_argument('-s', '--sources', nargs='+', choices=SOURCES, default=['artist'],
                        help='Types of metadata that are considered')
    parser.add_argument('-r', '--threshold', default=10, type=int,
                        help='Tags with number of unique artists less than this value will not be considered for '
                             'annotations')
    args = parser.parse_args()

    annotations = {}
    for tag_type in args.types:
        tag_prefix = TYPE_PREFIXES.get(tag_type, tag_type)
        main(args.input, args.api_input, args.directory, tag_prefix, [tag_type], args.sources,
             annotations, args.threshold)

    annotations_to_df(annotations).to_csv(path.join(args.directory, args.prefix + '_annotations.csv'), sep='\t',
                                          quoting=csv.QUOTE_NONE, escapechar=' ', index=False)  # TODO: make it less hacky

