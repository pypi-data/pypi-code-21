import click
from halo import Halo
from icheckin import connections, constants

@click.command('update', short_help='check for updates')
def command():
   click.echo('Current version: %s' % constants.VERSION)
   spinner = Halo(text='Checking for updates')
   spinner.start()
   update = connections.update_status()
   if update == True:
      spinner.succeed('Up to date.')
   elif update == False:
      spinner.fail('Failed.')
   else:
      spinner.warn('A newer version (%s) is available.' % update)
      click.echo('$ pip install --upgrade icheckin')
