# -*- coding: utf-8 -*-
#!/usr/bin/env python
'''
cgutils sequences
==================
Commands for manipulating file sequences. This command is relative to your current working directory. So cd into a directory that has some file sequences and try out some of the following commands.

List file sequences
-------------------
::

    cgutils sequences show

Prints a list of file sequences including any missing frames. You can paste
this list of of missing frames directly into the framelist for a deadline
render submission to complete your image sequence.

Rename a file sequence
----------------------
::

    cgutils sequences rename

Prompts guide you through renaming allowing you to change all aspects
of the image sequence including base name, start frame, and extension.

Create a test sequence
----------------------
::

    cgutils sequences create

Prompts you to create a file sequence.::

    cgutils sequences create --folders

Prompts you to create a folder sequence.

Delete a sequence
-----------------
::

    cgutils sequences delete

Prompts you to delete a file sequence.
'''

import collections
import errno
import os
import re
from ..packages import click


def get_sequences():
    '''Returns a dict of file sequences in the current working directory.'''
    seq_expr = r'(?P<name>[^0-9]*?.*?)?(?P<seq>[0-9]+)(?!.*[0-9])((?P<suf>(\..*)+?)?(\.(?P<ext>\w{1,})))?'

    sequences = collections.defaultdict(list)
    files = (f for f in os.listdir('.') if os.path.isfile(f))
    for f in files:
        match = re.search(seq_expr, f)
        if not match:
            continue
        md = match.groupdict()
        md['name'] = '' if md['name'] is None else md['name']
        md['suf'] = '' if md['suf'] is None else md['suf']
        md['ext'] = '' if md['ext'] is None else md['ext']
        if md['seq']:
            sequences[(md['name'], md['suf'], md['ext'])].append(md['seq'])

    return sorted(sequences.iteritems())


def echo_sequences(sequences):
    '''Echos a list of sequences returned by get_sequences'''
    if not sequences:
        click.echo("No image sequences found.")
        raise click.Abort()

    click.echo("Found the following image sequences:\n")

    seq_template = "\t{}. {}[{}-{}]{}.{}"

    for i, ((name, suf, ext), n) in enumerate(sequences):
        start = min(n)
        end = max(n)
        click.echo(seq_template.format(i, name, start, end, suf, ext))

        seq = set([int(i) for i in n])
        full_seq = set(range(int(start), int(end)))
        missing = list(full_seq - seq)
        if missing:
            click.echo("\t\tmissing: {}".format(sorted(missing)))


@click.group()
def cli():
    '''Tools for handling batches of files and folders.'''


@cli.command()
@click.option('--folders', help='Create folders not files', is_flag=True)
@click.option('--name',
              prompt=("Input a name. Using # characters to represent image "
                      "sequence placement and length. For example:\n\n"
                      "    my_sequence.####.exr\n\n"),
              help='Name template')
@click.option('--start',
              prompt="Sequence start number?",
              help='Sequence start number',
              type=int)
@click.option('--number',
              prompt="How many files?",
              help='Number of files',
              type=int)
def create(folders, name, start, number):
    '''Create a sequence of files.'''

    seq_regex = r'[#]+'
    m = re.search(seq_regex, name)
    if not m:
        click.echo('Naming convention incorrect: Could not find #')
        click.Abort()

    s, e = m.start(), m.end()
    padding = e - s
    name = name[:s] + '{:0>%d}' % (padding) + name[e:]

    created = 0
    existed = 0
    for i in xrange(number):
        filepath = name.format(i + start)
        if folders:
            try:
                os.mkdir(filepath)
                created += 1
            except OSError as e:
                if e.errno == errno.EEXIST:
                    existed += 1
        else:
            with open(filepath, 'w+'):
                os.utime(filepath, None)
            created += 1

    if folders:
        click.echo('Created {} folders.'.format(created))
        click.echo('{} already existed.'.format(existed))
    else:
        click.echo('Created {} files.'.format(number))


@cli.command()
@click.option('--index', default=-1, help="Index of file sequence to rename")
@click.option('--name', default='', help="New base name for file sequence")
@click.option('--start', default=-1, help="New sequence start number")
def rename(index, name, start):
    '''Rename a file sequence.'''

    sequences = get_sequences()

    if index < 0:
        echo_sequences(sequences)
        index = click.prompt("Which sequence do you want to rename?", type=int)

    (old_name, old_suf, old_ext), old_n = sequences[index]

    if not name:
        name = click.prompt(
            "Input a new name. Using # characters to represent image sequence "
            "placement and length. For example:\n\n"
            "    my_sequence.####.exr\n\n")

    seq_regex = r'[#]+'
    m = re.search(seq_regex, name)
    if not m:
        click.echo('Naming convention incorrect: Could not find #')
        click.Abort()

    s, e = m.start(), m.end()
    padding = e - s
    name = name[:s] + '{:0>%d}' % (padding) + name[e:]

    if start < 0:
        start = click.prompt(
            "Sequence start number?",
            default=min(old_n), type=int)

    click.echo("### Attempting to rename! ###")
    click.echo('    name:         {}'.format(name))
    click.echo('    start number: {}'.format(start))
    click.echo()

    otmp = "{}{}{}.{}"
    old_n = sorted(old_n)
    numbers = [int(i) for i in old_n]
    n_delta = numbers[0] - int(start)
    for i, n in zip(numbers, old_n):
        old = otmp.format(old_name, n, old_suf, old_ext)
        new = name.format(i - n_delta)
        try:
            os.rename(old, new)
            click.echo('          {} --> {}'.format(old, new))
        except Exception:
            click.echo('##ERROR## {} --> {}'.format(old, new))


@cli.command()
def show():
    '''Show all file sequences in your cwd.'''

    echo_sequences(get_sequences())


@cli.command()
def delete():
    '''Delete a file sequence.'''

    sequences = get_sequences()
    echo_sequences(sequences)
    index = click.prompt("\nChoose a sequence to delete", type=int)
    click.confirm('Are you sure?')

    (old_name, old_suf, old_ext), old_n = sequences[index]

    name_template = "{}{}{}.{}"
    indices = sorted(old_n)

    click.echo('### Attempting to delete sequence ###')
    for i in indices:
        filepath = name_template.format(old_name, i, old_suf, old_ext)
        try:
            os.remove(filepath)
            click.echo('Removed: {}'.format(filepath))
        except:
            click.echo('##ERROR## Failed to remove: {}'.format(filepath))

    click.echo('### Done! ###')

if __name__ == '__main__':
    cli()
