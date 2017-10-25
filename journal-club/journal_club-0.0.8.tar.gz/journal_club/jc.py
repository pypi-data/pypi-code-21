import pandas as pd
import numpy as np
import os
import time
import sys
from journal_club.sound import *
from journal_club.jc_algorithm import algorithm
from journal_club import where_jc

def _input(x):
    try:
        return raw_input(x)
    except NameError:
        return input(x)

here = os.path.dirname(__file__)
countdown_mp3 = os.path.join(where_jc, 'countdown.wav')

def save(r, record_csv):
    update(r).to_csv(record_csv)

def get_record(record_csv):
    try:
        record = pd.read_csv(record_csv).set_index('name')
    except IOError:
        raise IOError("{} does not exist create a new record with `jc [--record_csv filename] create name1 name2`")
    return update(record)

def update(record):
    r = record.copy()
    r.fillna(0, inplace=True)
    r = algorithm(r)
    return r

def pretty_choose(record, duration=5, freq=10):
    choices = np.random.choice(record.index, p=record.weight, size=duration*freq)
    max_len = max(map(len, record.index.values))
    times = np.arange(len(choices))**3.
    times /= times.sum()
    times *= duration

    template = '\rchoosing the next leader: {}'
    play_sound(countdown_mp3, 32-duration, block=False)
    previous = 0
    for i, (t, name) in enumerate(zip(times, choices)):
        time.sleep(t)
        if i == len(choices) - 1:
            template = "\r{}... your number's up"
        txt = template.format(name)
        sys.stdout.write(txt)
        gap = (previous - len(txt))
        if gap > 0:
            sys.stdout.write(' ' * gap)
        sys.stdout.flush()
        previous = len(txt)
    print()
    return name


def show_probabilities(record):
    record.sort_values('weight', ascending=False, inplace=True)
    for i, (name, r) in enumerate(record.iterrows()):
        print('{}. {} = {:.1%}'.format(i+1, name, r.weight))


def choose(args):
    attend = args.attendences
    record = get_record(args.record_csv)
    all_names = list(set(record.index.values.tolist() + attend))
    record = update(record.loc[all_names])
    names = record.index.values if attend is None else attend

    for n in set(all_names) - set(names):
        record.loc[n, 'misses'] += 1

    subset = record.loc[names]
    subset = update(subset)
    show_probabilities(subset)
    choice = pretty_choose(subset)
    record.loc[choice, 'turns'] += 1
    record.loc[names, 'attendences'] += 1

    record['meetings_since_turn'] += 1
    record.loc[choice, 'meetings_since_turn'] -= 1
    save(record, args.record_csv)
    play_text("{}, your number's up".format(choice))


def show(args):
    show_probabilities(get_record(args.record_csv))


def create(args):
    t = pd.DataFrame(columns=['name', 'turns', 'misses', 'attendences', 'meetings_since_turn', 'weight'])
    t['name'] = args.names
    t['turns'] = [0]*len(t)
    t['misses'] = [0]*len(t)
    t['attendences'] = [0]*len(t)
    t['meetings_since_turn'] = [0]*len(t)
    t['weight'] = 1. / len(t)
    t = t.set_index('name')
    if os.path.exists(args.record_csv):
        yn = _input('overwrite previous records? (press enter to continue)')
        save(t, args.record_csv)
        print("overwriting records at {}".format(args.record_csv))
    else:
        save(t, args.record_csv)
        print("created new record at {}".format(args.record_csv))


def main():
    import argparse
    parser = argparse.ArgumentParser('jc')
    subparsers = parser.add_subparsers()

    from os.path import expanduser, join
    home = expanduser("~")

    parser.add_argument('--record_csv', default=os.path.join(home, 'jc_record.csv'), help='record file location')

    create_parser = subparsers.add_parser('create', help='create a new record file in the current directory')
    create_parser.add_argument('names', nargs='+')
    create_parser.set_defaults(func=create)

    show_parser = subparsers.add_parser('show', help='shows the current record state')
    show_parser.set_defaults(func=show)

    choose_parser = subparsers.add_parser('choose', help='run the choosertron and pick a person from the given list (attendences)')
    choose_parser.add_argument('attendences', nargs='+', help='the people that are in attendence')
    choose_parser.set_defaults(func=choose)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()