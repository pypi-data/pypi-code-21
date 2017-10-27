import os
import click

from . import APP_DIR

@click.group(invoke_without_command=True, chain=True)
@click.option('-e', is_flag=True, help='open config in editor')
@click.pass_context
def config(ctx, e):
    """
    Configure juantap
    """
    if e:
        click.edit(filename=os.path.join(APP_DIR, 'config.ini'))
    else:
        click.echo(ctx.get_help())