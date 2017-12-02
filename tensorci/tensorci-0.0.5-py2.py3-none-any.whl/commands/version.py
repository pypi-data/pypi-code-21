import click
from tensorci import log
from tensorci.version import version as v


@click.command()
def version():
  log(v)