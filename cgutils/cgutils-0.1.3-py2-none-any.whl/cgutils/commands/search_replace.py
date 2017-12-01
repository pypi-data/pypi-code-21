# -*- coding: utf-8 -*-
#!/usr/bin/env python
'''
cgutils search_replace
======================
Find a pattern in all filenames in the current directory and replace it. Be careful...

Usage::

    cgutils search_replace new old

Here a file named new.01.exr in the current working directory would be renamed to old.01.exr.
'''

from ..packages import click
import sys
import os


def search_replace_file(root, f, search_str, replace_str):
    if search_str in f:

        source = os.path.join(root, f)
        dest_name = f.replace(search_str, replace_str)
        dest = os.path.join(root, dest_name)

        try:
            os.rename(source, dest)
            print '    {} -> {}'.format(f, dest_name)
        except OSError:
            print '    FAILED ', '{} -> {}'.format(f, dest_name)


def search_replace(search_str, replace_str, root, recursive=False):
    '''Find all files with search_str and replace it with replace_str'''
    if not recursive:

        print '\nINSIDE: ', root

        for f in os.listdir(root):

            if not os.path.isfile(f):
                continue

            search_replace_file(root, f, search_str, replace_str)

        return

    for root, subdirs, files in os.walk(root):

        print '\nINSIDE: ', root

        for f in files:
            search_replace_file(root, f, search_str, replace_str)


@click.command()
@click.argument('search_str')
@click.argument('replace_str')
@click.option('--recursive', is_flag=True, help='Walk the tree below the cwd')
def cli(search_str, replace_str, recursive=False):
    '''Find a pattern in all filenames in the current directory and replace it.

    Example::

        cgutils search_replace new old

    Here a file named new.01.exr would be renamed to old.01.exr
    '''

    confirm_msg = 'Search for {} and replace with {}?'
    do_it = click.confirm(confirm_msg.format(search_str, replace_str))
    if not do_it:
        return

    recursive_do_it = click.confirm(
            'Recursive search and replace is dangerous, are you REALLY sure '
            'you want to continue?'
        )

    if not recursive_do_it:
        return

    search_replace(
        search_str,
        replace_str,
        root=os.getcwd(),
        recursive=recursive
    )


if __name__ == '__main__':
    cli()
