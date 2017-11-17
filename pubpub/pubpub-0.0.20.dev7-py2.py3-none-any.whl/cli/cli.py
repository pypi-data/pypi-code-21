import click

from . import commands as c


@click.group()
@click.version_option(None, '-v', '--version')
@click.help_option('-h', '--help')
def entry_point():
  pass


# entry_point.add_command(c.pdf)
# entry_point.add_command(c.process_notebooks)
# entry_point.add_command(check.check)
# entry_point.add_command(c.cleanup)
entry_point.add_command(c.html)
entry_point.add_command(c.toc)
entry_point.add_command(c.update_styles)
entry_point.add_command(c.latex)
entry_point.add_command(c.template)
entry_point.add_command(c.pdflatex)
entry_point.add_command(c.create_snapshots)
