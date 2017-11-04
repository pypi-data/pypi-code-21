# -*- coding: utf-8 -*-
import os
import sys


def line_endings(fname):
    """Return all line endings in the file.
    """
    _endings = {line[-2:] for line in open(fname, 'rb').readlines()}
    res = set()
    for e in _endings:
        if e.endswith('\r'):
            res.add('\r')
        elif e.endswith('\r\n'):
            res.add('\r\n')
        elif e.endswith('\n'):
            res.add('\n')
    return res


def chomp(s):
    """Remove line terminator if it exists.
    """
    if s[-2:] == '\r\n':
        return s[:-2]
    if s[-1:] == '\r' or s[-1:] == '\n':
        return s[:-1]
    return s


def fix_line_endings(fname, eol='\n'):
    """Change all line endings to ``eol``.
    """
    lines = [chomp(line) for line in open(fname, 'rb').readlines()]
    with open(fname, 'wb') as fp:
        for line in lines:
            fp.write(line + eol)


def copy(ctx, source, dest, force=False):
    if source == dest:
        return

    source = os.path.normcase(os.path.normpath(str(source)))
    dest = os.path.normcase(os.path.normpath(str(dest)))
    flags = ""
    if sys.platform == 'win32':
        if force:
            flags += " /Y"
        # print 'copy {flags} {source} {dest}'.format(**locals())
        ctx.run('copy {flags} {source} {dest}'.format(**locals()))
    else:
        if force:
            flags += " --force"
        ctx.run('cp {flags} {source} {dest}'.format(**locals()))


def concat(ctx, dest, *sources, **kw):
    force = kw.pop('force', False)
    flags = ""
    if sys.platform == 'win32':
        if force:
            flags += " /Y"
        source = '+'.join(sources)
        ctx.run('copy {flags} {source} {dest}'.format(**locals()))
    else:
        if force:
            pass
            # flags += " --force"
        source = ' '.join(sources)
        # print 'cat {flags} {source} > {dest}'.format(**locals())
        ctx.run('cat {flags} {source} > {dest}'.format(**locals()))

    if len(line_endings(dest)) > 1:
        fix_line_endings(dest)
