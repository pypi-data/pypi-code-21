import click

from .check import commands as check
from .run import commands as run


@click.group()
def entry_point():
  pass


entry_point.add_command(check.check)
entry_point.add_command(run.run)
