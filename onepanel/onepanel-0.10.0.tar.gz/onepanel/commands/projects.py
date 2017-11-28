""" Command line interface for the OnePanel Machine Learning platform

'Projects' commands group.
"""

import os
import configobj
import json
import re
import click
from prettytable import PrettyTable
from onepanel.commands.login import login_required
from onepanel.gitwrapper import GitWrapper


class Project:
    """ Projects data model
    """

    PROJECT_FILE = '.onepanel/project'
    EXCLUSIONS = os.getenv('GIT_EXCLUSIONS', '.onepanel/project, .onepanel/logs/').split(', ')

    def __init__(self, account_uid=None, project_uid=None):
        self.account_uid = account_uid
        self.project_uid = project_uid

    def save(self, home):
        if not os.path.exists(home):
            os.makedirs(home)
        onepanel_dir = os.path.join(home, '.onepanel')
        if not os.path.exists(onepanel_dir):
            os.makedirs(onepanel_dir)
        project_file = os.path.join(home, Project.PROJECT_FILE)
            
        cfg = configobj.ConfigObj(project_file)
        cfg['uid'] = self.project_uid
        cfg['account_uid'] = self.account_uid
        cfg.write()

    @classmethod
    def from_json(cls, data):
        project = cls(data['account']['uid'], data['uid'])
        return project

    @classmethod
    def from_directory(cls, home):
        if not Project.exists_local(home):
            return None

        project_file = os.path.join(home, Project.PROJECT_FILE)
        cfg = configobj.ConfigObj(project_file)
        project = cls(cfg['account_uid'], cfg['uid'])
        return project

    @staticmethod
    def is_uid_valid(uid):
        pattern = re.compile('^[a-z0-9][-a-z0-9]{1,23}[a-z0-9]$')
        if pattern.match(uid):
            return True
        else:
            return False

    @staticmethod
    def exists_local(home):
        project_file = os.path.join(home, Project.PROJECT_FILE)
        if os.path.isfile(project_file):
            return True
        else:
            return False

    @staticmethod
    def exists_remote(project_uid, data):
        exists = False
        for item in data:
            if item['uid'] == project_uid:
                exists = True
                break
        return exists

    @staticmethod
    def print_list(data):
        if len(data) == 0:
            print('No projects found')
            return

        tbl = PrettyTable(border=False)
        tbl.field_names = ['NAME', 'INSTANCES', 'JOBS']
        tbl.align = 'l'
        for row in data:
            tbl.add_row([row['uid'], row['instanceCount'], row['jobCount']])
        print(tbl)


def create_project(ctx, account_uid, home):
    """ Project creation method for 'projects_init' and 'projects_create'
    commands
    """

    conn = ctx.obj['connection']

    if not account_uid:
        account_uid = conn.account_uid

    project_uid = os.path.basename(home)
    if not Project.is_uid_valid(project_uid):
        click.echo('Project name {} is invalid.'.format(project_uid))
        click.echo('Name should be 3 to 25 characters long, lower case alphanumeric or \'-\'\n'
                   'must start and end with an alphanumeric character.')
        return None

    url = '{}/projects'.format(conn.URL, account_uid)
    r = conn.get(url)
    if r.status_code == 200:
        remote_list = r.json()
    else:
        print('Error: {}'.format(r.status_code))
        return None

    project = None
    if Project.exists_remote(project_uid, remote_list):
        if Project.exists_local(home):
            click.echo('Project already initialized')
        else:
            project = Project(account_uid, project_uid)
            project.save(home)
            git = GitWrapper()
            git.init(home, account_uid, project_uid)
            git.exclude(home, Project.EXCLUSIONS)

    else:
        can_create = True
        if Project.exists_local(home):
            can_create = click.confirm(
                'Project does not exists for {}, create the project and overwrite?'
                .format(account_uid))

        if can_create:
            url = '{}/accounts/{}/projects'.format(conn.URL, account_uid)
            data = {
                'uid': project_uid
            }
            r = conn.post(url, data=json.dumps(data))

            if r.status_code == 200:
                project = Project.from_json(r.json())
                project.save(home)
                git = GitWrapper()
                git.init(home, account_uid, project_uid)
                git.exclude(home, Project.EXCLUSIONS)
            else:
                print('Error: {}'.format(r.status_code))

    return project

@click.group(help='Project commands group')
@click.pass_context
def projects(ctx):
    pass


@projects.command('list', help='Display a list of all projects.')
@click.pass_context
@login_required
def projects_list(ctx):
    conn = ctx.obj['connection']
    url = '{}/projects'.format(conn.URL)

    r = conn.get(url)
    if r.status_code == 200:
        Project.print_list(r.json())
    elif r.status_code == 404:
        print('No projects found')
    else:
        print('Error: {}'.format(r.status_code))


@click.command('init', help='Initialize project in current directory.')
@click.option('--account',
              help='Project is created and initialized for this account_uid.')
@click.pass_context
@login_required
def projects_init(ctx, account):
    home = os.getcwd()
    if not Project.is_uid_valid(os.path.basename(home)):
        project_uid = click.prompt('Please enter a valid project name')
        home = os.path.join(home, project_uid)

    if create_project(ctx, account, home):
        click.echo('Project is initialized in current directory.')


@projects.command('create', help='Create project in new directory.')
@click.option('--name',
              prompt='Name', default=os.path.basename(os.getcwd()),
              help='Project uid.')
@click.option('--account',
              help='Project is created and initialized for this account_uid.')
@click.pass_context
@login_required
def projects_create(ctx, name, account):
    home = os.path.join(os.getcwd(), name)
    if create_project(ctx, account, home):
        click.echo('Project is created in directory {}.'.format(home))


@click.command('clone', help='Clone <account_uid>/<uid> project from server.')
@click.argument('path', type=click.Path())
@click.argument('directory', type=click.Path(), required=False)
@click.pass_context
@login_required
def projects_clone(ctx, path, directory):
    conn = ctx.obj['connection']
    
    values = path.split('/')
    if len(values) == 2:
        account_uid, project_uid = values
    else:
        click.echo('Invalid project path. Please use <account_uid>/<uid>')
        return

    # check project path, account_uid, project_uid
    if directory is None:
        home = os.path.join(os.getcwd(), project_uid)
    elif directory == '.':
        home = os.getcwd()
    else:
        home = os.path.join(os.getcwd(), directory)

    # check if the project exisits
    r = conn.get('{}/projects'.format(conn.URL, account_uid))
    if r.status_code == 200:
        remote_list = r.json()
    else:
        print('Error: {}'.format(r.status_code))
        return

    if not Project.exists_remote(project_uid, remote_list):
        click.echo('There is no project {}/{} on the server'.format(account_uid, project_uid))
        return

    can_create = True
    if Project.exists_local(home):
        can_create = click.confirm('Project already exists, overwrite?')
    if not can_create:
        return

    # git clone
    git = GitWrapper()
    if git.clone(home, account_uid, project_uid) == 0:
        Project(account_uid, project_uid).save(home)
        git.exclude(home, Project.EXCLUSIONS)

@click.command('push', help='Push changes to onepanel repository')
@click.pass_context
@login_required
def projects_push(ctx):
    home = os.getcwd()
    GitWrapper().push(home)


@click.command('pull', help='Pull changes from onepanel repository (fetch and merge)')
@click.pass_context
@login_required
def projects_pull(ctx):
    home = os.getcwd()
    GitWrapper().pull(home)

