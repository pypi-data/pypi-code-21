import functools
import os
import subprocess as sp
import sys

import click
import requests
import yaml

try:
    from colorama import Style
    DIM = Style.DIM
    RESET = Style.RESET_ALL
except ImportError:
    DIM = RESET = ''


CONF_FILE = os.path.expanduser('~/.config/pag')


def run(cmd, echo=True, graceful=True):
    click.echo('  $ ' + " ".join(cmd))
    proc = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.STDOUT)
    output, _ = proc.communicate()
    output = output.decode('utf-8')
    if echo:
        click.echo(DIM + output + RESET)
    if not graceful and proc.returncode != 0:
        sys.exit(1)
    return proc.returncode, output


def die(msg, code=1):
    click.echo(msg)
    sys.exit(code)


def in_git_repo():
    # TODO -- would be smarter to look "up" the tree, too.
    if not os.path.exists('.git') or not os.path.isdir('.git'):
        return None
    return os.getcwd().split('/')[-1]


def assert_local_repo(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        if not in_git_repo():
            die("fatal:  Not a git repository")
        return func(*args, **kwargs)
    return inner


def eager_command(func):
    """Decorator for an option callback that should abort man command.

    Useful when an option completely changes the execution flow.
    """
    @functools.wraps(func)
    def inner(ctx, param, value):
        if not value or ctx.resilient_parsing:
            return
        func(ctx)
        ctx.exit()
    return inner


def get_default_upstream_branch(name):
    url = 'https://pagure.io/api/0/projects'
    response = requests.get(url, params=dict(pattern=name, fork=False))
    if not bool(response):
        raise IOError("Failed to talk to %r %r", (url, response))
    data = response.json()
    projects = data['projects']
    if not projects:
        raise ValueError("No such project %r" % name)
    if len(projects) > 1:
        raise ValueError("More than one project called %r found "
                         "(%i of them, in fact)." % (name, len(projects)))
    project = projects[0]
    return project['default_branch']


def get_current_local_branch():
    code, stdout = run(['git', 'branch', '--contains'])
    return stdout.split(maxsplit=1)[1].strip()


def repo_url(name, ssh=False, git=False, domain='pagure.io'):
    if ssh:
        prefix = 'ssh://git@'
    else:
        prefix = 'https://'

    if '/' in name:
        if git:
            suffix = 'forks/%s' % name
        else:
            suffix = 'fork/%s' % name
    else:
        suffix = '%s' % name

    if git:
        suffix = suffix + '.git'

    return prefix + domain + '/' + suffix


def create_config():
    username = input("FAS username:  ")
    conf = dict(
        username=username,
    )

    with open(CONF_FILE, 'wb') as f:
        f.write(yaml.dump(conf).encode('utf-8'))

    click.echo("Wrote %r" % CONF_FILE)


def load_config():
    with open(CONF_FILE, 'rb') as f:
        return yaml.load(f.read().decode('utf-8'))

def load_or_create_config():
    if not os.path.exists(CONF_FILE):
        click.echo("%r not found.  Creating..." % CONF_FILE)
        create_config()
    return load_config()


def configured(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        config = load_or_create_config()
        return func(config, *args, **kwargs)
    return inner
