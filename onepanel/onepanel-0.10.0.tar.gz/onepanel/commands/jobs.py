"""
Job commands
"""
import os
import sys
import json
from prettytable import PrettyTable

import click
import websocket

from onepanel.commands.login import login_required
from onepanel.commands.projects import Project


class Job:
    """
    Data model
    """

    uid = str
    machine_type = str
    environment = str
    project = Project

    def __init__(self, uid=None, project=None):

        self.uid = uid
        self.project = project


@click.group(help='Job commands group')
@click.pass_context
def jobs(ctx):

    # Retrieve the project from the local storage and pass it over
    local_project = Project.from_directory(os.getcwd())
    if local_project is None:
        # All job commands require project_uid. Return error before reaching them:
        print('This project is not initialized, type "onepanel init" to initialize this project')
        sys.exit(1)
    else:
        ctx.obj['project'] = local_project


@jobs.command('create', help='Execute a command on a remote machine in the current project')
@click.argument(
    'command',
    type=str
)
@click.option(
    '-m', '--machine-type',
    type=str,
    required=True,
    help='Machine type ID'
)
@click.option(
    '-e', '--environment',
    type=str,
    required=True,
    help='Instance template ID'
)
@click.pass_context
@login_required
def create_job(ctx, command, machine_type, environment):

    conn = ctx.obj['connection']
    project = ctx.obj['project']

    request_data = {
        'command': command,
        'machineType': {
            'uid': machine_type
        },
        'instanceTemplate': {
            'uid': environment
        }
    }

    url = '{root}/accounts/{account_uid}/projects/{project_uid}/jobs'.format(
        root=conn.URL,
        account_uid=project.account_uid,
        project_uid=project.project_uid
    )

    r = conn.post(url, data=json.dumps(request_data))
    if r.status_code == 200:
        resp = r.json()
    else:
        print('Error: {}'.format(r.status_code))
        return

    job_uid = resp['uid']

    print('New job created: {}'.format(job_uid))

    return job_uid


@jobs.command('list', help='Show commands executed on remote machines')
@click.option(
    '-a', '--all',
    type=bool,
    is_flag=True,
    default=False,
    help='Include finished commands'
)
@click.pass_context
@login_required
def list_jobs(ctx, all):

    conn = ctx.obj['connection']
    project = ctx.obj['project']

    account_uid = project.account_uid
    project_uid = project.project_uid

    # Request

    url = '{root}/accounts/{account_uid}/projects/{project_uid}/jobs{params}'.format(
        root=conn.URL,
        account_uid=account_uid,
        project_uid=project_uid,
        params='?running=true' if not all else ''
    )

    r = conn.get(url)
    if r.status_code == 200:
        resp = r.json()
    else:
        print('Error: {}'.format(r.status_code))
        return

    # Make a summary table

    if len(resp) == 0:
        print('No jobs. Use "--all" flag to retrieve completed jobs.')
        return None

    summary = PrettyTable(border=False)
    summary.field_names = ['ID', 'COMMAND']
    summary.align = 'l'
    for job in resp:
        summary.add_row([job['uid'], job['command']])
    print(summary)

    return [job['uid'] for job in resp]


@jobs.command('stop', help='Stop a job')
@click.argument(
    'job_uid',
    type=str
)
@click.pass_context
@login_required
def kill_job(ctx, job_uid):

    conn = ctx.obj['connection']
    project = ctx.obj['project']

    url = '{root}/accounts/{account_uid}/projects/{project_uid}/jobs/{job_uid}'.format(
        root=conn.URL,
        account_uid=project.account_uid,
        project_uid=project.project_uid,
        job_uid=job_uid
    )

    r = conn.delete(url)
    c = r.status_code
    if c == 200:
        print('Job stopped: {}'.format(job_uid))
        return True
    elif c == 404:
        print('Job not found: {}'.format(job_uid))
    else:
        print('Error: {}'.format(c))

    return False


@jobs.command('log', help='Show a log of the command')
@click.argument(
    'job_uid',
    type=str
)
@click.pass_context
@login_required
def job_log(ctx, job_uid):

    conn = ctx.obj['connection']
    project = ctx.obj['project']

    url = '{root}/accounts/{account_uid}/projects/{project_uid}/jobs/{job_uid}/logs'.format(
        root=conn.URL,
        account_uid=project.account_uid,
        project_uid=project.project_uid,
        job_uid=job_uid
    )

    r = conn.get(url)
    c = r.status_code

    if c == 200:

        resp_text = r.text
        # Response contains escaped characters. E.g., r.content is:
        # b'"rm: cannot remove \'README.md\': No such file or directory\\n"'
        # Clean them first
        log_lines = resp_text[1:-1].split('\\n')
        print('\n'.join(log_lines), end='')
        return True

    elif c == 400:

        # Streaming via WebSocket
        # See https://pypi.python.org/pypi/websocket-client/

        streaming_url = '{ws_root}/accounts/{account_uid}/projects/{project_uid}/jobs/{job_uid}/logs?access_token={token}&tail_lines=1'.format(
            ws_root='wss://c.onepanel.io/api',
            account_uid=project.account_uid,
            project_uid=project.project_uid,
            job_uid=job_uid,
            token=conn.token
        )

        ws = websocket.WebSocketApp(
            url=streaming_url,
            header=conn.headers,
            on_message=lambda ws, message: print(message, end=''),
            on_error=print
        )
        ws.run_forever()

    elif c == 404:

        print('Job not found: {}'.format(job_uid))

    else:

        print('Error: {}'.format(c))

    return False

