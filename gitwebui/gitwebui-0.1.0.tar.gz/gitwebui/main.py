#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import sys
import webbrowser

import click
from flask import Flask
from gitwebui import __version__
from gitwebui.blueprint import BlueGitWebUi, MONO_REPOS, MULTI_REPOS

app = Flask(__name__)

@click.command()
@click.option('-p', '--port', default=5000, help='port for listen')
@click.option('-h', '--host', default='0.0.0.0')
@click.option('-m', '--mode', default='mono', type=click.Choice(['mono', 'multi']))
@click.option('--viewonly', is_flag=True, help='view only')
@click.option('--nobrowser', is_flag=True, help='not load web browser')
@click.argument('path', default='')
@click.version_option(version=__version__, prog_name='gitwebui')
def main(port='5000', host='0.0.0.0', path='', mode='mono', nobrowser=True, viewonly=True):
    """run gitwebui: web ihm for a git repository """
    if not path:
        app.config['REPO_ROOT'] = os.path.abspath(os.getcwd())
    else:
        app.config['REPO_ROOT'] = os.path.abspath(path)
    if mode == 'mono':
        if not os.path.isdir(os.path.join(app.config['REPO_ROOT'], '.git')):
            click.echo(click.style('path is not a git repository valid', fg='red'), err=True)
            sys.exit(1)
        app.register_blueprint(BlueGitWebUi(mode=MONO_REPOS, viewonly=viewonly))
    else:
        app.register_blueprint(BlueGitWebUi(mode=MULTI_REPOS, viewonly=viewonly))
    if not nobrowser:
        webbrowser.open('http://%s:%s/' % (host, port))
    app.run(host=host, port=port)

if __name__ == "__main__":
    main()
