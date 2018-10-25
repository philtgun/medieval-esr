import pandas as pd

dictionary_filename = 'data/BRM-emot-submit.csv'
default_infile = 'results/vartags_good.csv'


def get_words(filename=dictionary_filename):
    df = pd.read_csv(filename)
    return set(df.Word)


def get_intersection(words, filename=default_infile):
    df = pd.read_csv(filename)
    tags = set(df.Tags)
    common_tags = tags.intersection(words)
    print('{} > {}'.format(len(tags), len(common_tags)))


if __name__ == '__main__':
    words = get_words()
    get_intersection(words)
