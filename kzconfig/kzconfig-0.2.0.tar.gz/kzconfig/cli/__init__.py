"""
kzconfig.cli
~~~~~

Kazoo config library.

A sup cli command for invoking sup against a remote kazoo container.
"""

import click

from ..sup import sup, sup_api


@click.command()
@click.option('--kube', 'method', flag_value='kube', default=True)
@click.option('--api', 'method', flag_value='api')
@click.argument('module')
@click.argument('function')
@click.argument('args', nargs=-1)
def sup_cmd(method, module, function, args):
    if method == 'api':
        func = sup_api
    else:
        func = sup
    return click.echo(func(module, function, *args))
