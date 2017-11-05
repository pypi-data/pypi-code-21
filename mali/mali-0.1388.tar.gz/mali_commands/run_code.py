import click
import requests
from .commons import add_to_data_if_not_none, output_result


@click.group('code')
def runcode_commands():
    pass


@runcode_commands.command('create')
@click.pass_context
@click.option('--name', required=True)
@click.option('--git', required=True)
@click.option('--org', required=False)
def code_create(ctx, name, git, org):
    data = {}

    add_to_data_if_not_none(data, name, "name")
    add_to_data_if_not_none(data, git, "git")
    add_to_data_if_not_none(data, org, "org")

    result = ctx.obj.handle_api(ctx.obj, requests.post, 'runcode', data)

    output_result(ctx, result, ['ok'])
