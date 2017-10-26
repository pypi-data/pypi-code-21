'''
Transforming Olympia ids to/from string and int
'''

from functools import lru_cache

import string
import re
import random

letters = string.ascii_lowercase
letters2 = 'abcdfghjkmnpqrstvwxz'  # the cut-down list that Olympia uses

letter2_to_int = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'f': 4, 'g': 5, 'h': 6,
                  'j': 7, 'k': 8, 'm': 9, 'n': 10, 'p': 11, 'q': 12, 'r': 13,
                  's': 14, 't': 15, 'v': 16, 'w': 17, 'x': 18, 'z': 19}


def _i(c):
    return ord(c) - 97


def to_oid(oid_int):
    oid_int = str(oid_int)
    if not oid_int.isdigit():
        raise ValueError('expected an integer, got '+oid_int)
    oid_int = int(oid_int)

    if oid_int < 10000:  # character or item
        return str(oid_int)
    elif oid_int < 50000:  # location
        oid_int -= 10000
        lets = oid_int // 100
        residue = oid_int % 100
        first = lets // 20
        second = lets % 20
        return letters2[first] + letters2[second] + '{:02d}'.format(residue)
    elif oid_int < 56760:  # CCN
        oid_int -= 50000
        lets = oid_int // 10
        residue = oid_int % 10
        first = lets // 26
        second = lets % 26
        return letters[first] + letters[second] + str(residue)
    elif oid_int < 58760:  # CNN
        oid_int -= 56760
        residue = oid_int % 100
        first = oid_int // 100
        return letters2[first] + '{:02d}'.format(residue)
    elif oid_int < 59000:
        return str(oid_int)
    elif oid_int < 79000:  # CNNN
        oid_int -= 59000
        residue = oid_int % 1000
        first = oid_int // 1000
        return letters2[first] + '{:03d}'.format(residue)
    else:  # storms, controlled units, etc
        return str(oid_int)


def to_int_safely(oid):
    try:
        ret = to_int(oid)
    except ValueError:
        ret = '0'
    return ret


@lru_cache(maxsize=None)
def to_int(oid):
    oid = str(oid)
    # re.fullmatch is python 3.4+
    if re.match(r'\A[a-z][a-z]\d\Z', oid):  # CCN
        return str(_i(oid[0])*26*10 + _i(oid[1])*10 + int(oid[2]) + 50000)
    elif re.match(r'\A[a-z][a-z]\d\d\Z', oid):  # CCNN, location
        return str(letter2_to_int[oid[0]]*20*100 + letter2_to_int[oid[1]]*100 + int(oid[2:]) + 10000)
    elif re.match(r'\A[a-z]\d\d\Z', oid):  # CNN
        return str(letter2_to_int[oid[0]]*100 + int(oid[1:]) + 56760)
    elif re.match(r'\A[a-z]\d\d\d\Z', oid):  # CNNN
        return str(letter2_to_int[oid[0]]*1000 + int(oid[1:]) + 59000)
    elif re.match(r'\A\d{1,5}\Z', oid):  # N through NNNNN
        return str(oid)
    elif re.match(r'\A1\d\d\d\d\d\Z', oid):  # 1NNNNN
        return str(oid)
    elif oid.isdigit():
        return str(oid)
    else:
        raise ValueError('invalid id value: '+oid)

oid_kinds = {
    'NNNN': {'start': 1000, 'end': 9999},  # structures
    'CCNN': {'start': 10000, 'end': 49999},  # map squares
    'CCN':  {'start': 50000, 'end': 56759},  # faction
    'CNN':  {'start': 56760, 'end': 58759},  # cities
    # region: 58760-58999
    'CNNN': {'start': 59000, 'end': 78999},  # catchall loc, default
    'NNNNN': {'start': 79000, 'end': 14999},  # npcs, storms, etc
}


def allocate_oid(data, oid_kind):
    if oid_kind not in oid_kinds:
        raise ValueError

    tries = 0
    while True:
        oid = random.randrange(oid_kinds[oid_kind]['start'], oid_kinds[oid_kind]['end'])
        if oid not in data:
            break
        tries += 1
        if tries > 10000:
            raise ValueError

    return str(oid)
