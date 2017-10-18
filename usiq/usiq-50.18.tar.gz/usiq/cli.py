import os
import sys
import yaml
from contextlib import contextmanager
from logbook import info, warning

from usiq import tagger, parser, renamer


class UsiqError(Exception):
    pass


def show(fname):
    info(tagger.get_tagger(fname))


def tag(fnames, args):
    default_tags = {key: args['--' + key]
                    for key in tagger.FIELDS
                    if '--' + key in args and args['--' + key] is not None}

    if args['--import']:
        with open_file_or_stdinout(args['--import']) as f:
            filetags = yaml.load(f)
    else:
        filetags = {}

    for fname in fnames:
        abs_fname = os.path.abspath(fname)
        tags = filetags[abs_fname] if abs_fname in filetags else {}
        tags.update(default_tags.copy())
        if args['--pattern']:
            tags.update(parser.parse_filename(fname, args['--pattern']))

        info('Setting tags {} on file {}'.format(tags, fname))
        if not args['--dry']:
            tagger.set_multiple_tags(fname, tags, prefix='')


def rename(fnames, args):
    pattern = args['--pattern']
    if illegal_pattern(pattern):
        raise UsiqError('Illegal pattern, aborting')

    for fname in fnames:
        tags = tagger.get_tagger(fname)
        new_fname = renamer.create_filename(tags, pattern)
        _, extension = os.path.splitext(fname)
        new_fname += extension
        target_exists = os.path.exists(new_fname)
        if target_exists:
            warning('Not moving {} -> {}, target file exists!'
                    .format(fname, new_fname))
            continue
        info('Moving {} -> {}'.format(fname, new_fname))
        if not args['--dry']:
            os.makedirs(os.path.dirname(new_fname), exist_ok=True)
            os.rename(fname, new_fname)


def export(fnames, args):
    outfile = args['--output']
    with open_file_or_stdinout(outfile, 'w') as f:
        yaml.dump({os.path.abspath(fname): tagger.get_tagger(fname).todict()
                   for fname in fnames},
                  f,
                  default_flow_style=False)


def illegal_pattern(pattern):
    constant = len(parser.get_fields(pattern)) == 0
    _, extension = os.path.splitext(pattern)
    has_extension = extension.lower() in ['.mp3', '.flac', '.ogg', '.m4a']
    return constant or has_extension


def with_config(args):
    if os.path.exists(args['--config']):
        with open(args['--config']) as f:
            cfg = yaml.load(f)
    else:
        cfg = {}
    for key, value in args.items():
        if key not in cfg:
            cfg[key] = value
        elif value is not None:
            cfg[key] = value
    return cfg


@contextmanager
def open_file_or_stdinout(fname, mode='r', **kwargs):
    if fname == '-':
        if 'r' in mode:
            yield sys.stdin
        elif 'w' in mode or 'a' in mode:
            yield sys.stdout
        else:
            yield sys.stdin
    else:
        f = open(fname, mode, **kwargs)
        yield f
        f.close()
