import click

from .check import commands as check
from .pdf import commands as pdf


@click.group()
def entry_point():
  pass


entry_point.add_command(check.check)
entry_point.add_command(pdf.pdf)
