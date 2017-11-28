# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *
from collections import defaultdict, OrderedDict
from itertools import combinations
import re

def condense(ss_unescaped):
    """
    Given multiple strings, returns a compressed regular expression just
    for these strings

    >>> condense(['she', 'he', 'her', 'hemoglobin'])
    'he(moglobin|r)?|she'
    """
    def estimated_len(longg, short):
        return (3
                + len(short)
                + sum(map(len, longg))
                - len(longg)
                * (len(short) - 1)
                - 1 )

    def stupid_len(longg):
        return sum(map(len, longg)) + len(longg)

    ss = [re.escape(s) for s in set(ss_unescaped)]
    ss.sort(key=len)

    short2long = defaultdict(lambda: {'p':[],'s':[]})

    for short, longg in combinations(ss, 2):
        if longg.startswith(short):
            short2long[short]['p'].append(longg)
        if longg.endswith(short):
            short2long[short]['s'].append(longg)

    short2long = sorted(list(short2long.items()),
                        key=lambda x: len(x[0]),
                        reverse=True)

    output = []
    objs = set(ss)

    for s, pre_sur in short2long:
        pp = set(pre_sur['p']) & objs
        ss = set(pre_sur['s']) & objs
        if ((stupid_len(pp) - estimated_len(pp, s))
            < (stupid_len(ss) - estimated_len(ss, s))):
            reg = (r'({heads})?{surfix}'
                    .format(surfix=s,
                           heads='|'.join(sorted([p[:-len(s)] for p in ss],
                           key=len,
                           reverse=True))))
            assert len(reg) == estimated_len(ss, s)
            output.append(reg)
            objs -= (ss | set([s]))
        elif ((stupid_len(pp) - estimated_len(pp, s))
            > (stupid_len(ss) - estimated_len(ss, s))):
            reg = (r'{prefix}({tails})?'
                .format(prefix=s,
                        tails='|'.join(sorted([p[len(s):] for p in pp],
                        key=len,
                        reverse=True))))
            assert len(reg) == estimated_len(pp, s)
            output.append(reg)
            objs -= (pp | set([s]))

    for residual in objs:
        output.append(residual)
    return re.sub(r'\(([^)])\)\?', r'\1?', r'|'.join(output))

def is_solid(regex):
    """
    Check the given regular expression is solid.

    >>> is_solid(r'a')
    True
    >>> is_solid(r'[ab]')
    True
    >>> is_solid(r'(a|b|c)')
    True
    >>> is_solid(r'(a|b|c)?')
    True
    >>> is_solid(r'(a|b)(c)')
    False
    >>> is_solid(r'(a|b)(c)?')
    False
    """

    shape = re.sub(r'(\\.|[^\[\]\(\)\|\?\+\*])', '#', regex)
    skeleton = shape.replace('#', '')
    if len(shape) <= 1:
        return True
    if re.match(r'^\[[^\]]*\][\*\+\?]?$', shape):
        return True
    if re.match(r'^\([^\(]*\)[\*\+\?]?$', shape):
        return True
    if re.match(r'^\(\)#*?\)\)', skeleton):
        return True
    else:
        return False

def is_packed(regex):
    """
    Check if the regex is solid and packed into a pair of parens
    """
    return is_solid(regex) and regex[0] == '('

def consolidate(regex):
    """
    Put on a pair of parens (with no catch tag) outside the regex,
    if the regex is not yet consolidated
    """
    if is_solid(regex):
        return regex
    else:
        return '({})'.format(regex)

def danger_unpack(regex):
    """
    Remove the outermost parens

    >>> unpack(r'(abc)')
    'abc'
    >>> unpack(r'(?:abc)')
    'abc'
    >>> unpack(r'(?P<xyz>abc)')
    'abc'
    >>> unpack(r'[abc]')
    '[abc]'
    """

    if is_packed(regex):
        return re.sub(r'^\((\?(:|P<.*?>))?(?P<content>.*?)\)$', r'\g<content>', regex)
    else:
        return regex

def unpack(regex):
    """
    Remove the outermost parens, keep the (?P...) one

    >>> unpack(r'(abc)')
    'abc'
    >>> unpack(r'(?:abc)')
    'abc'
    >>> unpack(r'(?P<xyz>abc)')
    '(?P<xyz>abc)'
    >>> unpack(r'[abc]')
    '[abc]'
    """
    if is_packed(regex) and not regex.startswith('(?P<'):
        return re.sub(r'^\((\?:)?(?P<content>.*?)\)$', r'\g<content>', regex)
    else:
        return regex

def parallel(regex_list, sort=False):
    """
    Join the given regexes using r'|'
    if the sort=True, regexes will be sorted by lenth before processing
    
    >>> parallel([r'abc', r'def'])
    'abc|def'
    >>> parallel([r'abc', r'd|ef'])
    'abc|def'
    >>> parallel([r'abc', r'(d|ef)'])
    'abc|d|ef'
    >>> parallel([r'abc', r'defg'])
    'defg|abc'
    """
    if sort:
        regex_list = sorted(regex_list, key=len, reverse=True)
    return '|'.join([unpack(regex) for regex in regex_list])

def nocatch(regex):
    """
    Put on a pair of parens (with no catch tag) outside the regex,
    if the regex is not yet packed;
    modified the outmost parens by adding nocatch tag
    """
    if is_solid(regex) and not is_packed(regex):
        return regex
    else:
        return '(?:{})'.format(danger_unpack(regex))

def concat(regex_list):
    """
    Concat multiple regular expression into one, if the given regular expression is not packed,
    a pair of paren will be add.

    >>> reg_1 = r'a|b'
    >>> reg_2 = r'(c|d|e)'
    >>> concat([reg_1, reg2])
    (a|b)(c|d|e)
    """
    output_list = []

    for regex in regex_list:
        output_list.append(consolidate(regex))
    return r''.join(output_list)

def nocatchall(regex):
    """
    Return a regex with all parens has a no catch tag
    """
    return re.sub(r'(?<!\\)(?P<leading>(\\\\)*)\((\?(:|P<.*?>))?', r'\g<leading>(?:', regex)

def option(regex):
    """
    return a regex has a option tag

    >>> option(r'[ab]')
    '[ab]?'
    >>> option(r'(abc)')
    '(abc)?'
    >>> option('abc')
    '(abc)?'
    """

    return nocatch(regex) + '?'
