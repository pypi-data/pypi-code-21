from click import globals
from cookiecutter import repository, vcs, utils, cli, config
from cookiecutter.config import get_user_config
from jinja2.ext import Extension
import sys
import os

def get_zip_dir(clone_dir, template):
    if repository.is_repo_url(template):
        identifier = zip_uri.rsplit('/', 1)[1]
        zip_path = os.path.join(clone_to_dir, identifier)
    else:
        zip_path = os.path.abspath(template)
    return zip_path

def get_repo_dir(clone_dir, template):
    repo_type, repo_url = cookiecutter.vcs.identify_repo(repo_url)
    repo_url = repo_url.rstrip('/')
    tail = os.path.split(repo_url)[1]
    if repo_type == 'git':
        repo_dir = os.path.normpath(os.path.join(clone_to_dir,
                                                 tail.rsplit('.git')[0]))
    elif repo_type == 'hg':
        repo_dir = os.path.normpath(os.path.join(clone_to_dir, tail))
    return repo_dir

def find_repo_dir(
        template, checkout=None, no_input=False, extra_context=None,
        replay=False, overwrite_if_exists=False, output_dir='.',
        config_file=None, default_config=False, password=None, **extra_args):
    config_dict = get_user_config(
        config_file=config_file,
        default_config=default_config,
    )
    template = repository.expand_abbreviations(template, config_dict['abbreviations'])
    clone_dir = os.path.expanduser(config_dict['cookiecutters_dir'])
    repository_canidates = []
    if repository.is_zip_file(template):
        repository_canidates = [ get_zip_dir(template) ]
    elif repository.is_repo_url(template):
        repository_canidates = [ get_repo_dir(template) ]
    else:
        repository_canidates = [ template, os.path.join(clone_dir) ]

    for repo_canidate in repository_canidates:
        if repository.repository_has_cookiecutter_json(repo_canidate):
            return repo_canidate
    return None

class RepoExtensions(Extension):

    def __init__(self, environment):
        super(Extension, self).__init__()
        # now comes the hacky part
        ctx = globals.get_current_context(silent=True)
        if ctx:
            params = {}.update(ctx.params)
            repo_dir = find_repo_dir(**ctx.params)
            if repo_dir:
                sys.path.insert(0, os.path.join(repo_dir, "extensions"))

