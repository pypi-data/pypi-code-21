# -*- coding: utf-8 -*-
import sys
import click
from tpcli.cli import pass_context


@click.command('delete', short_help='delete entry from Teampass')
@click.option('--item', 'type', flag_value='item', default=True, help='delete item')
@click.option('--folder', 'type', flag_value='folder', help='delete folder with sub-folders and items')
@click.option('--id', required=True, help='entry id')
@pass_context
def cli(ctx, type, id):
    """Delete entry from Teampass."""
    try:
        data = ctx.tp.delete(type, id)
    except Exception as ex:
        ctx.logerr(ex)
        sys.exit(1)
    else:
        ctx.log("Output: {}".format(data))
