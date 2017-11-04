# -*- coding: utf-8 -*-

from dktasklib.wintask import task


@task(default=True)
def help(ctx):
    """
    """
    ctx.run('invoke --help')


@task(default=True)
def list(ctx):
    """Show help, basically an alias for --help.
    This task can be removed once the fix to this issue is released:
    https://github.com/pyinvoke/invoke/issues/180
    """
    ctx.run('invoke --list')
