import click
import functools
from .printer import Printer


@click.command()
@click.option('-d', '--directory', 'directory', type=click.Path())
@click.option(
    '-f', '--file', 'files', envvar='FILES', multiple=True, type=click.Path())
@click.option('-o', '--ouput', 'output', default='/tmp/pubpub')
@click.option('-v', '--virtualenv_name', 'virtualenv_name')
@click.option('-c', '--copy', 'copy', multiple=True, type=click.Path())
@click.option('-w', '--working-dir', 'working_dir', default="/tmp")
@click.option('-t', '--template', 'template', default="article.tplx")
@click.option('-d', '--debug', count=True)
@click.pass_context
def run(ctx, directory, files, output, virtualenv_name, copy, working_dir,
        template, debug):
  """Runs printer"""
  printer = Printer(
      copy=copy,
      debug=debug,
      output=output,
      files=files,
      directory=directory,
      working_dir=working_dir,
      template=template,
      virtualenv_name=virtualenv_name)
  printer.run()
