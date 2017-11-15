import click

from .check import commands as check
from .pdf import commands as pdf
from .html import commands as html


@click.group()
def entry_point():
  pass


entry_point.add_command(check.check)
entry_point.add_command(pdf.pdf)
entry_point.add_command(pdf.process_notebooks)
entry_point.add_command(pdf.cleanup)
entry_point.add_command(pdf.html)
entry_point.add_command(pdf.toc)
entry_point.add_command(pdf.update_styles)
entry_point.add_command(pdf.latex)
entry_point.add_command(pdf.create_template)
