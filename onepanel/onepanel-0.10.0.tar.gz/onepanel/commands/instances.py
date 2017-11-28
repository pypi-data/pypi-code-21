"""
Instance ("application") module
"""
import re

import click
import sys

from onepanel.commands.base import APIViewController
from onepanel.commands.login import login_required


class InstanceViewController(APIViewController):

    def __init__(self, conn):
        
        super(InstanceViewController, self).__init__(conn)

        project = self.get_project()

        self.endpoint = '{root}/accounts/{account_uid}/projects/{project_uid}/instances'.format(
            root=self.conn.URL,
            account_uid=project.account_uid,
            project_uid=project.project_uid
        )


@click.group(help='App (instance) commands group')
@click.pass_context
def apps(ctx):
    ctx.obj['vc'] = InstanceViewController(ctx.obj['connection'])


@apps.command(
    'create',
    help='Create a new application. The app\'s UID: Max 25 chars, lower case alphanumeric or "-", '
         'must start and end with alphanumeric'
)
@click.argument(
    'app_uid',
    type=str
)
@click.option(
    '-m', '--machine-type',
    type=str,
    required=True,
    help='Machine type ID. Call "onepanel machine_types list" for IDs.'
)
@click.option(
    '-e', '--environment',
    type=str,
    required=True,
    help='Instance template ID. Call "onepanel environments list" for IDs.'
)
@click.option(
    '-s', '--storage',
    type=str,
    required=True,
    help='Storage type ID.'
)
@click.pass_context
@login_required
def create_instance(ctx, app_uid, machine_type, environment, storage):

    instance_uid = app_uid
    machine_type_uid = machine_type
    instance_template_uid = environment
    volume_type_uid = storage

    pattern = re.compile('^[a-z0-9][-a-z0-9]{1,23}[a-z0-9]$')
    if not pattern.match(instance_uid):
        print(
            'Incorrect ID. ID must be:',
            '1. Maximum 25 chars',
            '2. Lower case alphanumeric or "-"',
            '3. Start and end with alphanumeric',
            sep='\n'
        )
        sys.exit(1)

    new_instance = {
        'uid': instance_uid,
        'machineType': {
            'uid': machine_type_uid
        },
        'volumeType': {
            'uid': volume_type_uid
        },
        'instanceTemplate': {
            'uid': instance_template_uid
        }
    }

    created_instance = ctx.obj['vc'].post(post_object=new_instance)

    if created_instance:
        print('New app ID: {}'.format(created_instance['uid']))


@apps.command('list', help='Show active applications in the current project')
@click.pass_context
@login_required
def list_instances(ctx):

    vc = ctx.obj['vc']
    items = vc.get()
    vc.print_items(items, fields=['uid'], field_names=['UID'])


@apps.command('terminate', help='Terminate the app')
@click.argument(
    'app_uid',
    type=str
)
@click.pass_context
@login_required
def terminate_instance(ctx, app_uid):

    ctx.obj['vc'].delete(app_uid, message_on_success='Application terminated')
