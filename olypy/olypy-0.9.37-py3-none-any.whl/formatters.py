'''
Helper functions for reading/writing Olympia lib files
'''

import sys
from functools import partial
from collections import OrderedDict


def fixed(count, char, key, array):
    if not array or len(array) == 0:
        return
    if len(array) % count != 0:
        raise ValueError(key + ' array is of incorrect length')

    print(key, end='')
    print(char, end='')

    while True:
        chunk = array[:count]
        print(' '.join([str(i) for i in chunk]), end='')
        array = array[count:]
        if array:
            print(' \\\n\t', end='')
        else:
            break
    print()


def print_list(array, first, rest):
    if len(array) > first:
        chunk = array[:first]
        array = array[first:]
        print(' '.join([str(i) for i in chunk]), end=' ')  # yes, we want the trailing space
        if array:
            print('\\\n\t', end='')
    while len(array) > rest:
        chunk = array[:rest]
        array = array[rest:]
        print(' '.join([str(i) for i in chunk]), end=' ')  # yes, we want the trailing space
        if array:
            print('\\\n\t', end='')
    print(' '.join([str(i) for i in array]), end=' \n')  # yes, we want the trailing space


def default_print(key, array):
    if not array or len(array) == 0:
        return
    if key != 'firstline':
        print(key, end=' ')
    print(' '.join([str(i) for i in array]))


def boxlist_print(key, array):
    if not array or len(array) == 0:
        return
    print(key, end='')
    if key[-1] != '\t':
        print(end=' ')
    print_list(array, 9, 11)
    return


def boxlist_print_pd(key, array):
    if len(array) < 4 or len(array) > 6:
        raise ValueError('array must be of length 4 to 6')
    boxlist_print(key, array)
    return


def boxlist_print_tab(key, array):
    boxlist_print(key + '\t', array)


def known_print(key, array):
    if len(array) == 0:
        return
    print(key, end=' ')
    print_list(array, 10, 11)


def admit_print(key, arrayarray):
    if key != ' am':
        raise ValueError

    for array in arrayarray:
        if len(array) < 2:
            raise ValueError
        chunk = array[:2]
        array = array[2:]
        print(key, ' '.join([str(i) for i in chunk]), end=' ')
        if len(array):
            print_list(array, 7, 11)
        else:
            print()
    return


grand_format = OrderedDict([
    ('firstline', 1),
    ('na', 1),
    ('il', partial(fixed, 2, '\t')),
    ('tl', partial(fixed, 8, '\t')),
    ('an', boxlist_print),
    ('ad', boxlist_print),
    ('ah', boxlist_print),
    ('LI', OrderedDict([('wh', 1),
                        ('hl', boxlist_print)])),
    ('CH', OrderedDict([('ni', 1), ('lo', 1), ('pl', 1), ('he', 1), ('si', 1), ('lk', 1), ('lr', 1),
                        ('sl', partial(fixed,  5, '\t')),
                        ('pr', 1), ('mo', 1), ('bh', 1), ('gu', 1), ('tf', 1), ('bp', 1), ('ra', 1),
                        ('at', 1), ('df', 1), ('mi', 1), ('po', 1),
                        ('ct', boxlist_print),
                        ('dt', partial(fixed,  3, ' '))])),
    ('CM', OrderedDict([('im', 1), ('ma', 1), ('ca', 1), ('as', 1), ('hm', 1), ('qc', 1), ('rb', 1),
                        ('hs', 1), ('cm', 1), ('pr', 1), ('kw', 1), ('dg', 1), ('sr', 1), ('bf', 1),
                        ('vp', 1), ('pl', 1), ('pc', 1), ('ar', 1), ('ot', 1),
                        ('vi', known_print)])),
    ('LO', OrderedDict([('pd', boxlist_print_pd),
                        ('hi', 1), ('sh', 1), ('ba', 1), ('dg', 1), ('sl', 1), ('lc', 1)])),
    ('SL', OrderedDict([('te', boxlist_print),
                        ('da', 1), ('de', 1), ('ca', 1), ('bm', 1), ('er', 1), ('eg', 1), ('mo', 1),
                        ('gr', 1), ('sd', 1), ('cl', 1), ('sh', 1), ('mc', 1), ('op', 1), ('lo', 1),
                        ('cp', 1), ('uf', 1), ('sf', 1), ('ql', 1), ('td', 1),
                        ('nc', boxlist_print),
                        ('lt', boxlist_print),
                        ('lf', boxlist_print),
                        ('bs', boxlist_print),
                        ('lw', 1), ('lp', 1)])),
    ('IT', OrderedDict([('pl', 1), ('wt', 1), ('lc', 1), ('rc', 1), ('fc', 1), ('mu', 1), ('pr', 1),
                        ('an', 1), ('at', 1), ('df', 1), ('mi', 1), ('bp', 1), ('ca', 1), ('un', 1)])),
    ('IM', OrderedDict([('au', 1), ('cl', 1), ('cr', 1), ('cc', 1), ('uk', 1), ('qc', 1), ('ab', 1),
                        ('db', 1), ('mb', 1), ('ba', 1), ('rd', 1), ('tn', 1), ('oc', 1), ('ti', 1),
                        ('rc', 1), ('pc', 1), ('ct', 1), ('lo', 1), ('mu', 1), ('ms', 1)])),
    ('PL', OrderedDict([('fn', 1), ('em', 1), ('ve', 1), ('pw', 1), ('np', 1), ('fs', 1), ('ft', 1),
                        ('fo', 1), ('nt', 1), ('tf', 1), ('sl', 1), ('sb', 1), ('so', 1), ('dr', 1),
                        ('ci', 1), ('bm', 1), ('lt', 1),
                        ('kn', known_print),
                        ('un', boxlist_print),
                        ('uf', boxlist_print),
                        ('am', admit_print)])),
    ('SK', OrderedDict([('tl', 1), ('rs', 1),
                        ('of', boxlist_print),
                        ('re', boxlist_print),
                        ('rq', partial(fixed, 3, '\t')),
                        ('pr', 1), ('np', 1), ('ne', 1)])),
    ('GA', OrderedDict([('tl', 1), ('nj', 1), ('nu', 1), ('sk', 1), ('rh', 1)])),
    ('MI', OrderedDict([('sb', 1), ('di', 1), ('mc', 1), ('md', 1), ('ss', 1), ('ca', 1), ('gc', 1),
                        ('mh', 1), ('co', 1), ('ov', 1), ('ol', 1), ('bs', 1), ('sn', 1), ('ds', 1),
                        ('nm', known_print)])),
    ('CO', OrderedDict([('li', 1),
                        ('ar', partial(fixed,  8, ' ')),
                        ('cs', 1), ('wa', 1), ('st', 1), ('us', 1), ('ue', 1), ('de', 1), ('po', 1),
                        ('pr', 1), ('if', 1)])),
])

# these are things which are strings and not lists
# TODO: put this info into the table above
first_level_strings = set(('na',))
second_level_strings = set(('ds', 'li', 'pl', 'sn', 'fn', 'pw', 'em', 've'))


def print_one_thing(datum):
    key1s_seen = set()
    for key1, value1 in grand_format.items():
        if datum.get(key1) is None:
            continue
        key1s_seen.add(key1)

        if value1 == 1:
            default_print(key1, datum.get(key1))
        elif callable(value1):
            value1(key1, datum.get(key1))
        elif isinstance(value1, dict):
            print(key1)
            key2s_seen = set()
            for key2, value2 in value1.items():
                if datum[key1].get(key2) is None:
                    continue
                key2s_seen.add(key2)

                if value2 == 1:
                    default_print(' '+key2, datum[key1].get(key2))
                elif callable(value2):
                    value2(' '+key2, datum[key1].get(key2))
                else:
                    raise ValueError('unknown format value for subtype')
            if datum[key1].keys() != key2s_seen:
                extras = set(datum[key1].keys()).difference(key2s_seen)
                raise KeyError('saw extra key2s, key1={} extras={} datum={}'.format(key1, extras, datum))
        else:
            raise ValueError('unknown format value for type')
    print()
    if datum.keys() != key1s_seen:
        extras = set(datum.keys()).difference(key1s_seen)
        raise KeyError('saw extra key1s, extras={} datum={}'.format(extras, datum))


def read_oly_file(f, verbose=False):
    '''
    Unlike io.c, we gut it out :-) basically we don't know the details about this file
    format, we just GO GO GO. The copylib test & exceptions while printing make sure
    we did the right thing here.
    '''

    data = {}
    prev = ''
    box = ''
    subbox = ''

    if isinstance(f, str):
        f = open(f, 'r')

    for line in f:
        untrimmed_line = line
        line = line.rstrip()

        if line.startswith('#'):
            continue
        if prev:
            line = prev + line
            prev = ''
        new = line.rstrip(' \\')  # trailing \ and associated whitespace
        if new != line:
            prev = new
            continue
        else:
            line = new

        if line == '':
            box = ''
            subbox = ''
            continue

        pieces = line.split()
        what = pieces.pop(0)

        if not box:
            if line.startswith('\t') or line.startswith(' '):
                raise ValueError('line cannot start with whitespace')
            if what.isdigit():
                box = what
                data[box] = {}
                data[box]['firstline'] = [' '.join([what] + pieces)]
                continue
            else:
                raise ValueError('unknown first line')

        if len(what) == 2 and what.isupper():
            subbox = what
            data[box] = data.get(box, {})
            data[box][subbox] = data[box].get(subbox, {})
            continue

        if not(line.startswith('\t') or line.startswith(' ')):
            if data[box].get(what) is not None:
                raise ValueError('saw a non-continuation for an existing item')
            if what in first_level_strings:
                data[box][what] = [untrimmed_line[3:].rstrip('\n')]
            else:
                data[box][what] = pieces
            subbox = ''
        else:
            if what != 'am' and data[box].get(subbox).get(what) is not None:
                raise ValueError
            if what == 'am':
                am = data[box].get(subbox, {}).get('am', [])
                am.append(pieces)  # list of lists
                data[box][subbox]['am'] = am
            elif what in second_level_strings:
                data[box][subbox][what] = [untrimmed_line[4:].rstrip('\n')]
            else:
                data[box][subbox][what] = pieces

    if verbose:
        print('read', len(data), verbose, 'boxes.', file=sys.stderr)

    return data
