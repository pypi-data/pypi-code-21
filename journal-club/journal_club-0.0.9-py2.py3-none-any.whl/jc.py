import pandas as pd
import numpy as np
import os
import time
import sys
from os.path import expanduser, join, exists
from os import remove
from journal_club.sound import *
from journal_club.jc_algorithm import algorithm
from journal_club import where_jc

here = os.path.dirname(__file__)
countdown_mp3 = os.path.join(where_jc, 'countdown.wav')


def _input(x):
    try:
        return raw_input(x)
    except NameError:
        return input(x)


def save(r, record_csv):
    update(r).to_csv(record_csv)


def update(record):
    r = record.copy()
    r.fillna(0, inplace=True)
    r = algorithm(r)
    return r


def validate_file(args):
    if not exists(args.record_csv):
        raise IOError("Record csv {} does not exist.".format(args.record_csv))
    
    record = get_record(args)
    cols = ['turns', 'misses', 'attendences', 'meetings_since_turn', 'weight']
    missing = [i for i in cols if i not in record.columns]
    if missing:
        raise IOError("{} is not a valid record_csv file. {} columns are missing".format(args.record_csv, missing))
    return True


def create_new(args):
    t = pd.DataFrame(columns=['name', 'turns', 'misses', 'attendences', 'meetings_since_turn', 'weight'])
    t['name'] = args.attendences
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


def get_record(args):
    try:
        record = pd.read_csv(args.record_csv).set_index('name')
    except IOError:
        create_new(args)
        record = get_record(args)
    return update(record)


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
    record = get_record(args)
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
    print("Accessing database at {}".format(args.record_csv))
    show_probabilities(get_record(args))


def validate(args):
    validate_file(args)
    print("{} is a valid journal_club record_csv file.".format(args.record_csv))


def reset(args):
    validate_file(args)  # assertions
    input("Warning! Removing database file! Press ENTER to continue/ctrl+c to cancel ")
    remove(args.record_csv)
    print("File removed...")


def main():
    import argparse
    parser = argparse.ArgumentParser('jc')
    subparsers = parser.add_subparsers()

    home = expanduser("~")
    default_location = os.path.join(home, 'jc_record.csv')

    parser.add_argument('--record_csv', default=default_location, help='Record file location default={}'.format(default_location))

    show_parser = subparsers.add_parser('show', help='Shows the current record state')
    show_parser.set_defaults(func=show)

    choose_parser = subparsers.add_parser('choose', help='Run the choosertron and pick a person from the given list (attendences). '\
                                                          'Creates database if needed')
    choose_parser.add_argument('attendences', nargs='+', help='The people that are in attendence')
    choose_parser.set_defaults(func=choose)

    subparsers.add_parser('reset', help='Deletes the record file. Runs `rm RECORD_CSV`').set_defaults(func=reset)
    subparsers.add_parser('validate', help='Validates the record file.').set_defaults(func=validate)



    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()