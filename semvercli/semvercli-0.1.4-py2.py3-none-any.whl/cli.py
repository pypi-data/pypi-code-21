# -*- coding: utf-8 -*-

"""Console script for semvercli."""

import click
import semvercli
from .meta import __version__


@click.group()
@click.pass_context
def main(context):
    """Console script for semvercli."""
    pass


@main.command()
@click.argument('increment', default='major')
@click.argument('version', default='')
@click.pass_context
def bump(context, increment, version):
    print(semvercli.bump(increment, version))

@main.command()
@click.argument('v1')
@click.argument('v2')
@click.pass_context
def compare(context, v1, v2):
    print(semvercli.compare(v1, v2))

@main.command()
def version():
    print(__version__)

if __name__ == "__main__":
    main()
