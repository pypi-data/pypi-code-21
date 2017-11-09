# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import OrderedDict
from p4rr0t007.lib import l33t as l33tdict


word_mapping = [
    ('hacker', 'haxor'),
    ('elite', 'eleet'),
]

vowel_mapping = [
    ('A', '4'),
    ('a', '4'),
    ('E', '3'),
    ('e', '3'),
    ('I', '1'),
    ('i', '1'),
    ('O', '0'),
    ('o', '0'),
]


consonant_mapping = [
    ('T', '7'),
    ('t', '7'),
    ('B', '8'),
    ('b', '8'),
    ('G', '6'),
    ('g', '6'),
    ('S', '5'),
    ('s', '5'),
    ('Z', '2'),
    ('z', '2'),
    ('l', '1'),
    ('g', '9'),
]

ycnvd_options = {
    'capitalize': True,
    'extended': True,
    'reverse': True,
}


def tr4nsl33t(word, extended=True, basic=True, advanced=True, ultimate=False, UpperCase=False, LowerCase=False, capitalize=False, reverse=False):
    word = OrderedDict(word_mapping).pop(word.lower(), word)

    # enabling character mapping
    mapping = OrderedDict(vowel_mapping)

    if extended:
        mapping.update(consonant_mapping)

    if basic:
        mapping.update(l33tdict.basic)

    if advanced:
        mapping.update(l33tdict.advanced)

    if ultimate:
        mapping.update(l33tdict.ultimate)

    def translate(char):
        return mapping.get(char, char)

    r3sul7 = u''.join(map(translate, word))

    # transmogrification
    r3sul7 = ''.join(map(translate, word))

    # reversing
    if reverse:
        r3sul7 = r3sul7[::-1]

    # casing
    if capitalize:
        r3sul7 = r3sul7.capitalize()

    elif LowerCase:
        r3sul7 = r3sul7.lower()

    elif UpperCase:
        r3sul7 = r3sul7.upper()

    return r3sul7
