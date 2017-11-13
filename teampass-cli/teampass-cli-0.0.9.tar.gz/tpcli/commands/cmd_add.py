# -*- coding: utf-8 -*-
import sys
import click
from tpcli.cli import pass_context


@click.command('add', short_help='add entry to Teampass')
@click.option('--item', 'type', flag_value='item', default=True, help='add item')
@click.option('--folder', 'type', flag_value='folder', help='add folder')
@click.option('--title', required=True, help='title for new folder or label for new item')
@click.option('--login', help='login value for new item')
@click.option('--password', help='password value for new item (if empty generate random 16-symbols password with no no ambiguous option)')
@click.option('--description', help='description value for new item')
@click.option('--folder-id', required=True, help='parent folder id')
@click.option('--list', 'view', flag_value='list', default=True, help='format output as list')
@click.option('--table', 'view', flag_value='table', help='format output as table')
@pass_context
def cli(ctx, type, title, login, password, description, folder_id, view):
    """Add entry to Teampass."""
    if type == 'item':
        if not (login and description):
            ctx.logerr('Options --login, --description required')
            sys.exit(1)

    try:
        data = ctx.tp.add(type, title, login, password, description, folder_id)
    except Exception as ex:
        ctx.logerr(ex)
        sys.exit(1)
    else:
        if view == 'table':
            ctx.log(ctx.tp.print_result_table(data))
        elif view == 'list':
            ctx.log(ctx.tp.print_result_list(type, data))
