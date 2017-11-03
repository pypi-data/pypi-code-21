import click, os

import rdcgen
from rdcgen import utils

@click.group()
@click.option('--username', '-u', prompt='Username')
@click.password_option(confirmation_prompt=False)
@click.pass_context
def cli(ctx, username, password):
    ctx.obj = {'username': username, 'password': password}

@cli.command()
@click.argument('filename', required=False)
@click.pass_obj
def build(obj, filename):
    gt = rdcgen.GroupTree(filename) if filename else rdcgen.GroupTree()
    
    entry_gen = utils.entry_generator(obj['username'], obj['password'])
    servers = utils.server_generator(entry_gen)

    for path, server_name in servers:
        gt.merge_server(path, server_name, {})

    gt.save()
