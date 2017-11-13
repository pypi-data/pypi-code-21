#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import click
from tpcli.teampass import TeampassClient

CONTEXT_SETTINGS = dict(auto_envvar_prefix='TPCLI')


class Context(object):

    def log(self, msg, *args):
        """Logs a message to stdout."""
        if args:
            msg %= args
        click.echo(msg)

    def logerr(self, msg, *args):
        """Logs a message to stderr only if verbose is enabled."""
        if args:
            msg %= args
        click.echo(msg, err=True)


pass_context = click.make_pass_decorator(Context, ensure=True)
cmd_folder = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                          'commands'))


class ComplexCLI(click.MultiCommand):

    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(cmd_folder):
            if filename.endswith('.py') and \
               filename.startswith('cmd_'):
                rv.append(filename[4:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            if sys.version_info[0] == 2:
                name = name.encode('ascii', 'replace')
            mod = __import__('tpcli.commands.cmd_' + name,
                             None, None, ['cli'])
        except ImportError:
            return
        return mod.cli


@click.command(cls=ComplexCLI, context_settings=CONTEXT_SETTINGS)
@click.option('--api-endpoint',
              default=lambda: os.environ.get('TPCLI_ENDPOINT'),
              help='Teampass API endpoint.')
@click.option('--api-key', hide_input=True,
              default=lambda: os.environ.get('TPCLI_KEY'),
              help='Teampass API key.')
@pass_context
def cli(ctx, api_endpoint, api_key):
    """Console utility for Teampass."""
    ctx.tp = TeampassClient(api_endpoint, api_key)
