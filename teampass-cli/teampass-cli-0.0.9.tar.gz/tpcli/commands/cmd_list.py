# -*- coding: utf-8 -*-
import sys
import click
from tpcli.cli import pass_context


@click.command('show', short_help='show entry from Teampass')
@click.option('--item', 'type', flag_value='item', default=True, help='show items')
@click.option('--folder', 'type', flag_value='folder', help='show folders')
@click.option('--list', 'view', flag_value='list', default=True, help='format output as list')
@click.option('--table', 'view', flag_value='table', help='format output as table')
@click.option('--tree', 'view', flag_value='tree', help='format output as tree')
@pass_context
def cli(ctx, type, view):
    """List entry from Teampass."""
    try:
        data = ctx.tp.list(type)
    except Exception as ex:
        ctx.logerr(ex)
        sys.exit(1)
    else:
        if view == 'table':
            ctx.log(ctx.tp.print_result_table(data))
        elif view == 'list':
            ctx.log(ctx.tp.print_result_list(type, data))
        elif view == 'tree':
            if type == 'folder':
                ctx.log(ctx.tp.print_result_tree(data))
            else:
                ctx.logerr('Format output as tree is only available for the folder type')
