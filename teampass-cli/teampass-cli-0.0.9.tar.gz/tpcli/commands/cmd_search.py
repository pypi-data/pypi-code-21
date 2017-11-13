# -*- coding: utf-8 -*-
import sys
import click
from tpcli.cli import pass_context


@click.command('search', short_help='search entry in Teampass')
@click.option('--item', 'type', flag_value='item', default=True, help='search items')
@click.option('--folder', 'type', flag_value='folder', help='search folders')
@click.option('--list', 'view', flag_value='list', default=True, help='format output as list')
@click.option('--table', 'view', flag_value='table', help='format output as table')
@click.argument('text', required=True)
@pass_context
def cli(ctx, type, view, text):
    """Search entry in Teampass."""
    try:
        data = ctx.tp.search(type, text)
    except Exception as ex:
        ctx.logerr(ex)
        sys.exit(1)
    else:
        if view == 'table':
            ctx.log(ctx.tp.print_result_table(data))
        elif view == 'list':
            ctx.log(ctx.tp.print_result_list(type, data))
