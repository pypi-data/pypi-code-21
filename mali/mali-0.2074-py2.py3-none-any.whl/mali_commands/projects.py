# coding=utf-8
import click
import requests

from mali_commands.commons import add_to_data_if_not_none, create_validate_length, output_result
from mali_commands.options import project_id_option


@click.group('projects')
def projects_commands():
    pass


@projects_commands.command('list')
# deprecated option but some clients use it
@click.option('--outputFormat', '-o', type=click.Choice(['tables', 'json']), default='tables', required=False)
@click.pass_context
def list_projects(ctx, outputformat):
    ctx.obj.bad_json_format = outputformat == 'json'

    projects = ctx.obj.handle_api(ctx.obj, requests.get, 'projects')

    output_result(ctx, projects.get('projects', []), ['project_id', 'display_name', 'description', 'token', 'org'])


max_project_display_name = 140
min_project_display_name = 1

max_project_description = 140
min_project_description = 0


@projects_commands.command('create')
@click.option(
    '--displayName', required=True, callback=create_validate_length(min_project_display_name, max_project_display_name))
@click.option(
    '--description', required=False, callback=create_validate_length(min_project_description, max_project_description))
@click.option('--org', required=False)
# deprecated option but some clients use it
@click.option('--outputFormat', '-o', type=click.Choice(['tables', 'json']), default='tables', required=False)
@click.pass_context
def create_project(ctx, displayname, description, org, outputformat):
    ctx.obj.bad_json_format = outputformat == 'json'

    data = {}

    add_to_data_if_not_none(data, displayname, "display_name")
    add_to_data_if_not_none(data, org, "org")
    add_to_data_if_not_none(data, description, "description")

    result = ctx.obj.handle_api(ctx.obj, requests.post, 'projects', data)

    output_result(ctx, result, ['id', 'token'])


@projects_commands.command('transfer')
@project_id_option(required=True)
@click.option('--transferTo', required=False)
@click.pass_context
def transfer_project(ctx, projectid, transferto):
    data = {}

    add_to_data_if_not_none(data, transferto, "transfer_to")

    result = ctx.obj.handle_api(
        ctx.obj, requests.post, 'projects/{project_id}/transfer'.format(project_id=projectid), data)

    output_result(ctx, result, ['ok'])
