import click
from icheckin import credentials

@click.command('show', short_help='show saved credentials')
def command():
   if credentials.exist():
      credentials.display(credentials.read())
   else:
      click.echo('No saved credentials.')