""" Command line interface for the OnePanel Machine Learning platform

Entry point for command line interface.
"""

import os
import functools
import configparser
import click
import requests

from onepanel.commands.login import login, login_with_token
from onepanel.commands.projects import projects, projects_init, projects_clone, projects_push, projects_pull
from onepanel.commands.jobs import jobs
from onepanel.commands.machine_types import machine_types
from onepanel.commands.environments import environments
from onepanel.commands.instances import apps
from onepanel.commands.volume_types import volume_types
from onepanel.commands.data import data

class Connection:
    """ REST API requests defaults and credentials
    """
    def __init__(self):
        self.URL = os.getenv('BASE_API_URL', 'https://c.onepanel.io/api')
        self.SSL_VERIFY = True
        self.headers = {'Content-Type': 'application/json'}
        self.account_uid = None
        self.token = None

        # wrap requests methods to reduce number of arguments in api queries
        self.get = functools.partial(requests.get, headers=self.headers, verify=self.SSL_VERIFY)
        self.post = functools.partial(requests.post, headers=self.headers, verify=self.SSL_VERIFY)
        self.put = functools.partial(requests.put, headers=self.headers, verify=self.SSL_VERIFY)
        self.delete = functools.partial(requests.delete, headers=self.headers, verify=self.SSL_VERIFY)

    def save_credentials(self, data):
        credentials = configparser.ConfigParser()
        credentials['default'] = {'uid': data['uid'],
                                  'token': data['sessions'][0]['token'],
                                  'account_uid': data['account']['uid']}

        onepanel_home = os.path.expanduser(os.path.join('~', '.onepanel'))
        if not os.path.exists(onepanel_home):
            os.makedirs(onepanel_home)

        filename = os.path.join(onepanel_home, 'credentials')
        with open(filename, 'w') as f:
            credentials.write(f)

    def load_credentials(self):
        credentials = configparser.ConfigParser()
        filename = os.path.expanduser(os.path.join('~', '.onepanel', 'credentials'))
        credentials.read(filename)

        self.account_uid = credentials.get('default', 'account_uid', fallback=None)
        self.token = credentials.get('default', 'token', fallback=None)

        if self.token:
            self.headers['Authorization'] = 'Bearer {}'.format(self.token)


@click.group()
@click.pass_context
def cli(ctx):
    conn = Connection()
    conn.load_credentials()

    ctx.obj = {}
    ctx.obj['connection'] = conn


cli.add_command(login)
cli.add_command(login_with_token)
cli.add_command(projects_init)
cli.add_command(projects_clone)
cli.add_command(projects_push)
cli.add_command(projects_pull)
cli.add_command(projects)
cli.add_command(jobs)
cli.add_command(machine_types)
cli.add_command(environments)
cli.add_command(volume_types)
cli.add_command(apps)
cli.add_command(data)


if __name__ == '__main__':
    cli()
