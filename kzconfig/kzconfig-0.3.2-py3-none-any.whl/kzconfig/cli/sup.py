"""
kzconfig.cli.sup
~~~~~

Kazoo config library.

A sup cli command for invoking sup against a remote kazoo container.
"""

import click

from ..context import Context


@click.command()
@click.argument('module')
@click.argument('function')
@click.argument('args', nargs=-1)
def main(module, function, args):
    context = Context()
    return click.echo(context.sup.sup(module, function, *args))
