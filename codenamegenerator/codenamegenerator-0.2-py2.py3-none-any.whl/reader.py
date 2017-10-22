import csv
import os
import random

DICT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dicts')


def dictionary_sample(name, sample=1):
    # TODO: Cache counting, and use file.seek to speed file reading.

    fname = os.path.join(DICT_DIR, f'{name}.csv')

    if not os.path.exists(fname):
        raise ValueError(f'{name} dictionary does not exists.')

    with open(fname, 'rt') as csvfile:
        csvreader = csv.DictReader(
            csvfile,
            fieldnames=['NAME'],
            delimiter=',',
            quotechar='"')

        names = [row['NAME'] for row in csvreader]

    return random.sample(names, sample)
