import click
import requests

from pag.app import app
from pag.utils import (
    assert_local_repo,
    in_git_repo,
    repo_url,
    die,
    run
)


@app.group()
@assert_local_repo
def remote():
    pass

@remote.command()
@click.argument('name')
def add(name):
    repo = in_git_repo()
    url = repo_url(name + '/' + repo)
    response = requests.head(url)
    if not bool(response):
        die("No such url %s, %r" % (url, response))

    repo = in_git_repo()
    url = repo_url(name + '/' + repo, ssh=True, git=True)
    name = name.split('/')[0]
    return run(['git', 'remote', 'add', name, url])
