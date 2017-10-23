""" Command line interface for the OnePanel Machine Learning platform

'Login' commands group.
"""

import click
import json
from functools import wraps
from onepanel.gitwrapper import GitWrapper

@click.command()
@click.option('--email', prompt='Email')
@click.option('--password', prompt='Password', hide_input=True)
@click.pass_context
def login(ctx, email, password):
    conn = ctx.obj['connection']
    url = conn.URL + '/sessions'
    data = {
        'email': email,
        'password': password,
        'sessions': [
            {'device': 'cli'}
        ],
        'account': {}
    }

    r = conn.put(url, data=json.dumps(data))
    if r.status_code == 200:
        data = r.json()
        conn.save_credentials(data)
        GitWrapper().save_credentials(data['uid'], data['gitlab_impersonation_token'])
    elif r.status_code == 401 or r.status_code == 422:
        print('Incorrect username or password')
    else:
        print('Error: {}'.format(r.status_code))

@click.command()
@click.argument('token')
@click.pass_context
def login_with_token(ctx, token):
    conn = ctx.obj['connection']
    url = conn.URL + '/sessions'
    data = {
        'sessions': [
            {
                'token': token,
                'device': 'cli'
            }
        ]
    }

    r = conn.put(url, data=json.dumps(data))
    if r.status_code == 200:
        data = r.json()
        conn.save_credentials(data)
        GitWrapper().save_credentials(data['uid'], data['gitlab_impersonation_token'])
    elif r.status_code == 401 or r.status_code == 422:
        print('Invalid token')
    else:
        print('Error: {}'.format(r.status_code))

def login_required(func):
    """ Decorator that checks if the session is opened

    The decorator checks if the session is opened based on current context. Therefore please put the decorator
    after @click.pass_context decorator. For example:
        @click.command('hello')
        @click.option('--format')
        @click.pass_context
        @login_required
        def hello(ctx, format):
            ...
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if len(args) == 0:
            print('There is no context in the command. Please add @click.pass_context decorator')
            return

        ctx = args[0]
        conn = ctx.obj['connection']
        if conn.account_uid:
            return func(*args, **kwargs)
        else:
            print('You are not logged in, ' \
                'log in by typing `onepanel login` at command line.')
    return wrapper
