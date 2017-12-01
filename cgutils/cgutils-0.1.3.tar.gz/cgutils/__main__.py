#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import click
from . import commands


class LazyCLI(click.MultiCommand):
    '''Lazily imports interfaces from cgutils.commands package.'''

    def list_commands(self, ctx):
        cmds = [cmd for cmd in dir(commands) if not cmd.startswith('__')]
        return sorted(cmds)

    def get_command(self, ctx, name):
        cmd_module = getattr(commands, name)
        return cmd_module.cli


@click.group(cls=LazyCLI)
@click.pass_context
def cli(ctx):
    '''Command Line Tools for common tasks'''
    pass


if __name__ == '__main__':
    cli()
