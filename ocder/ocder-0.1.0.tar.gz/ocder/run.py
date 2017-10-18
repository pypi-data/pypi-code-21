#!/usr/bin/env python
from __future__ import absolute_import, print_function

import click
import sys

from ocder.ocder import check_target


@click.command()
@click.option('-j', '--jobs', default=1, type=int, help='Number of parallel jobs.')
@click.option('-f', '--fix', is_flag=True, help='Save fixes into checked files.')
@click.option('-v', '--verbose', count=True, help='Set verbosity level')
@click.argument('target')
def run(jobs, fix, target, verbose):
    """OCDer entry point.

    Check-only run should return non-zero status on errors.
    """
    valid = check_target(target, fix, jobs, verbose)
    if not valid and not fix:
        sys.exit(-1)


if __name__ == '__main__':
    run()
