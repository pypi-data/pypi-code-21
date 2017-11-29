# This file is part of tako
# Copyright (c) 2015-2017 Adam Hartz <hartz@mit.edu> and contributors
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# tako is a fork of xonsh (http://xon.sh)
# xonsh is Copyright (c) 2015-2016 the xonsh developers and is licensed under
# the 2-Clause BSD license.

import os
import re
import ast
import builtins

from takoshell.tools import (check_for_partial_string, RE_STRING_START,
                        iglobpath, levenshtein)

from takoshell.completers.tools import get_filter_function

PATTERN_NEED_QUOTES = r'\s`\$\{\}\,\*\(\)"\'\?&'
PATTERN_NEED_QUOTES = '[' + PATTERN_NEED_QUOTES + ']' + r'|\band\b|\bor\b'
PATTERN_NEED_QUOTES = re.compile(PATTERN_NEED_QUOTES)

def _path_from_partial_string(inp, pos=None):
    if pos is None:
        pos = len(inp)
    partial = inp[:pos]
    startix, endix, quote = check_for_partial_string(partial)
    _post = ""
    if startix is None:
        return None
    elif endix is None:
        string = partial[startix:]
    else:
        if endix != pos:
            _test = partial[endix:pos]
            if not any(i == ' ' for i in _test):
                _post = _test
            else:
                return None
        string = partial[startix:endix]
    end = re.sub(RE_STRING_START, '', quote)
    _string = string
    if not _string.endswith(end):
        _string = _string + end
    try:
        val = ast.literal_eval(_string)
    except SyntaxError:
        return None
    if isinstance(val, bytes):
        env = builtins.__tako_env__
        settings = env['TAKO_SETTINGS']
        val = val.decode(encoding=settings.encoding,
                         errors=settings.encoding_errors)
    return string + _post, val + _post, quote, end


def _normpath(p):
    """
    Wraps os.normpath() to avoid removing './' at the beginning
    and '/' at the end. On windows it does the same with backslashes
    """
    initial_dotslash = p.startswith(os.curdir + os.sep)
    p = p.rstrip()
    trailing_slash = p.endswith(os.sep)
    p = os.path.normpath(p)
    if initial_dotslash and p != '.':
        p = os.path.join(os.curdir, p)
    if trailing_slash:
        p = os.path.join(p, '')

    return p


def _startswithlow(x, start, startlow=None):
    if startlow is None:
        startlow = start.lower()
    return x.startswith(start) or x.lower().startswith(startlow)


def _startswithnorm(x, start, startlow=None):
    return x.startswith(start)


def _add_env(paths, prefix):
    if prefix.startswith('$'):
        key = prefix[1:]
        paths.update({'$' + k
                      for k in builtins.__tako_env__
                      if get_filter_function()(k, key)})


def _add_dots(paths, prefix):
    if prefix in {'', '.'}:
        paths.update({'./', '../'})
    if prefix == '..':
        paths.add('../')


def _add_cdpaths(paths, prefix):
    """Completes current prefix using CDPATH"""
    env = builtins.__tako_env__
    csc = env['TAKO_SETTINGS'].CASE_SENSITIVE_COMPLETIONS
    for cdp in env.get('CDPATH'):
        test_glob = os.path.join(cdp, prefix) + '*'
        for s in iglobpath(test_glob, ignore_case=(not csc)):
            if os.path.isdir(s):
                paths.add(os.path.basename(s))


def _quote_to_use(x):
    single = "'"
    double = '"'
    if single in x and double not in x:
        return double
    else:
        return single


def _quote_paths(paths, start, end):
    expand_path = builtins.__tako_expand_path__
    out = set()
    space = ' '
    backslash = '\\'
    double_backslash = '\\\\'
    orig_start = start
    orig_end = end
    need_quotes = any(re.search(PATTERN_NEED_QUOTES, x) or (backslash in x) for x in paths)
    for s in paths:
        start = orig_start
        end = orig_end
        if start == '' and need_quotes:
            start = end = _quote_to_use(s)
        if os.path.isdir(expand_path(s)):
            _tail = '/'
        elif end == '':
            _tail = space
        else:
            _tail = ''
        if start != '' and 'r' not in start and backslash in s:
            start = 'r%s' % start
        s = s + _tail
        if end != '':
            if "r" not in start.lower():
                s = s.replace(backslash, double_backslash)
            if s.endswith(backslash) and not s.endswith(double_backslash):
                s += backslash
        if end in s:
            s = s.replace(end, ''.join('\\%s' % i for i in end))
        out.add(start + s + end)
    return out


def _joinpath(path):
    # convert our tuple representation back into a string representing a path
    if path is None:
        return ''
    elif len(path) == 0:
        return ''
    elif path == ('',):
        return os.sep
    elif path[0] == '':
        return os.sep + _normpath(os.path.join(*path))
    else:
        return _normpath(os.path.join(*path))


def _splitpath(path):
    # convert a path into an intermediate tuple representation
    # if this tuple starts with '', it means that the path was an absolute path
    path = _normpath(path)
    if path.startswith(os.sep):
        pre = ('', )
    else:
        pre = ()
    return pre + _splitpath_helper(path, ())


def _splitpath_helper(path, sofar=()):
    folder, path = os.path.split(path)
    if path:
        sofar = sofar + (path, )
    if not folder or folder == os.sep:
        return sofar[::-1]
    return _splitpath_helper(folder, sofar)

def subsequence_match(ref, typed, csc):
    """
    Detects whether typed is a subsequence of ref.

    Returns ``True`` if the characters in ``typed`` appear (in order) in
    ``ref``, regardless of exactly where in ``ref`` they occur.  If ``csc`` is
    ``False``, ignore the case of ``ref`` and ``typed``.

    Used in "subsequence" path completion (e.g., ``~/u/ro`` expands to
    ``~/lou/carcohl``)
    """
    if csc:
        return _subsequence_match_iter(ref, typed)
    else:
        return _subsequence_match_iter(ref.lower(), typed.lower())


def _subsequence_match_iter(ref, typed):
    if len(typed) == 0:
        return True
    elif len(ref) == 0:
        return False
    elif ref[0] == typed[0]:
        return _subsequence_match_iter(ref[1:], typed[1:])
    else:
        return _subsequence_match_iter(ref[1:], typed)


def _expand_one(sofar, nextone, csc):
    out = set()
    for i in sofar:
        _glob = os.path.join(_joinpath(i), '*') if i is not None else '*'
        for j in iglobpath(_glob):
            j = os.path.basename(j)
            if subsequence_match(j, nextone, csc):
                out.add((i or ()) + (j, ))
    return out


def complete_path(prefix, line, start, end, ctx, cdpath=True):
    """Completes based on a path name."""
    # string stuff for automatic quoting
    path_str_start = ''
    path_str_end = ''
    p = _path_from_partial_string(line, end)
    lprefix = len(prefix)
    if p is not None:
        lprefix = len(p[0])
        prefix = p[1]
        path_str_start = p[2]
        path_str_end = p[3]
    tilde = '~'
    paths = set()
    env = builtins.__tako_env__
    settings = env['TAKO_SETTINGS']
    csc = settings.case_sensitive_completions
    for s in iglobpath(prefix + '*', ignore_case=(not csc)):
        paths.add(s)
    if len(paths) == 0 and settings.SUBSEQUENCE_PATH_COMPLETION:
        # this block implements 'subsequence' matching, similar to fish and zsh.
        # matches are based on subsequences, not substrings.
        # e.g., ~/u/ro completes to ~/lou/carcolh
        # see above functions for details.
        p = _splitpath(os.path.expanduser(prefix))
        if len(p) != 0:
            if p[0] == '':
                basedir = ('', )
                p = p[1:]
            else:
                basedir = None
            matches_so_far = {basedir}
            for i in p:
                matches_so_far = _expand_one(matches_so_far, i, csc)
            paths |= {_joinpath(i) for i in matches_so_far}
    if len(paths) == 0 and settings.FUZZY_PATH_COMPLETION:
        threshold = settings.SUGGEST_THRESHOLD
        for s in iglobpath(os.path.dirname(prefix) + '*', ignore_case=(not csc)):
            if levenshtein(prefix, s, threshold) < threshold:
                paths.add(s)
    if tilde in prefix:
        home = os.path.expanduser(tilde)
        paths = {s.replace(home, tilde) for s in paths}
    if cdpath:
        _add_cdpaths(paths, prefix)
    paths = _quote_paths({_normpath(s) for s in paths},
                         path_str_start,
                         path_str_end)
    _add_env(paths, prefix)
    _add_dots(paths, prefix)
    return paths, lprefix


def complete_dir(prefix, line, start, end, ctx, cdpath=False):
    o, lp = complete_path(prefix, line, start, end, cdpath)
    return {i for i in o if os.path.isdir(i)}, lp
