import csv
import numpy as np

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
    'auto2',
    'bmat',
    'team',
    'auto1',
    'artist',
    'mturk'
}


def read_data(filename=default_infile):
    tags_map = {}
    tag_types = set()
    tag_sources = set()
    track_ids = set()

    with open(filename) as fp:
        reader = csv.reader(fp)
        next(reader, None)  # skip header
        for track_id, tag_type, value, source in reader:
            tag_types.add(tag_type)
            tag_sources.add(source)
            if tag_type in accepted_types and source in accepted_sources:
                track_ids.add(track_id)
                if value not in tags_map:
                    tags_map[value] = set()
                tags_map[value].add(track_id)

    return tags_map, len(track_ids)


def get_top_tags(tags_map):
    tags = np.array(list(tags_map.keys()))
    counts = np.array([len(vals) for vals in tags_map.values()])
    map = counts.argsort()[::-1]
    return tags[map], counts[map]


def export_stats(tags, counts, filename=default_outfile):
    with open(filename, 'w') as fp:
        writer = csv.writer(fp)
        writer.writerow(['Tag', 'Count'])
        for tag, count in zip(tags, counts):
            writer.writerow([tag, count])


def print_tags(tags_map):
    for tag_value, track_ids in tags_map.items():
        print('{}: {}'.format(tag_value, len(track_ids)))


if __name__ == '__main__':
    data, total = read_data()
    print('Total: {}'.format(total))
    tags, counts = get_top_tags(data)
    export_stats(tags, counts)
