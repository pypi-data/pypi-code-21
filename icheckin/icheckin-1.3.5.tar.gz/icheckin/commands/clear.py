import click
from icheckin import credentials

@click.command('clear', short_help='clear all credentials')
def command():
   if credentials.exist():
      credentials.display(credentials.read(), 'Credentials to Clear')  
      if not credentials.empty():
         if click.confirm('Confirm?'):
            credentials.clear()
            click.echo('Successfully cleared.')
      else:
         click.echo('Nothing to clear.')
   else:
      click.echo('No saved credentials.')
