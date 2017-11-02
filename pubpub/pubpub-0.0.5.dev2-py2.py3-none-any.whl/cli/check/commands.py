import click
import functools
import logging
import os
from ...utils import package


def print_version(ctx, param, value):
  if not value or ctx.resilient_parsing:
    return
  click.echo(package.version)
  ctx.exit()


@click.command()
@click.option('-d', '--directory', 'directory', type=click.Path())
@click.option(
    '-f', '--file', 'files', envvar='FILES', multiple=True, type=click.Path())
@click.option('-v', '--virtualenv_name', 'virtualenv_name')
@click.option('-w', '--working-dir', 'working_dir', default="/tmp")
@click.option('-t', '--template', 'template', default="article.tplx")
@click.option('-d', '--debug', count=True)
@click.option(
    '--version',
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True)
@click.pass_context
def check(ctx, directory, files, virtualenv_name, working_dir, template,
          debug):
  """Check"""
  print("Checking...")
