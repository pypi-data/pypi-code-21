# -*- coding: utf-8 -*-
import sys
import click
from tpcli.cli import pass_context


@click.command('edit', short_help='edit entry in Teampass')
@click.option('--item', 'type', flag_value='item', default=True, help='add item')
@click.option('--folder', 'type', flag_value='folder', help='add folder')
@click.option('--id', required=True, help='entry id')
@click.option('--title', help='title for entry')
@click.option('--login', help='login value for entry')
@click.option('--password', help='password value for entry')
@click.option('--description', help='description value for entry')
@click.option('--folder-id', help='parent folder id')
@click.option('--list', 'view', flag_value='list', default=True, help='format output as list')
@click.option('--table', 'view', flag_value='table', help='format output as table')
@pass_context
def cli(ctx, type, id, title, login, password, description, folder_id, view):
    """Edit entry in Teampass."""
    try:
        data = ctx.tp.edit(type, id, title, login, password, description, folder_id)
    except Exception as ex:
        ctx.logerr(ex)
        sys.exit(1)
    else:
        if view == 'table':
            ctx.log(ctx.tp.print_result_table(data))
        elif view == 'list':
            ctx.log(ctx.tp.print_result_list(type, data))
