import click
import git
import os
import shutil

from .config import Config

pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@click.option('-s', '--source', default=None, help="Source to fetch templates.")
@pass_config
def template(config, source):
    """
    Template manager for quick prototyping.

    Examples of usage:

        template init vue-app my-view app
    """
    if source:
        config.default_source = source


@template.command(help="Initialise a project from a template.")
@click.argument('template-name', default=None, type=click.STRING)
@click.argument('dest', default=None, type=click.STRING, required=False)
@pass_config
def init(conf, template_name, dest):
    if not dest:
        dest = template_name

    git.Repo.clone_from(
        '{source}/{template}'.format(
            source=conf.default_source,
            template=template_name
        ),
        to_path=dest
    )

    click.secho('Deleting template .git', fg='yellow')
    shutil.rmtree(os.path.join(dest, '.git'))

    click.secho('Initializing new git repo', fg='green')
    git.Repo.init(path=dest)


@template.group()
@pass_config
def config(conf):
    pass


@config.command(help="List all.")
@pass_config
def list(conf):
    for k, v in conf.__dict__.items():
        click.echo("{} : {}".format(k, v))

@config.command(help="Edit configuration key")
@click.option('--default-source', help="Default source to fetch template")
@pass_config
def set(conf, default_source):
    conf.default_source = default_source
    conf.save()
