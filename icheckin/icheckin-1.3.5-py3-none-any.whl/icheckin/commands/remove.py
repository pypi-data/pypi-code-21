import sys
import click
from icheckin import credentials

@click.command('remove', short_help='remove credentials')
def command():
   if credentials.exist():
      creds = credentials.read()
      credentials.display(creds, 'Existing Credentials', 
         numbering=True)
      # Prompt for indexes        
      if not credentials.empty():
         click.echo('[Comma for multiple values]')
         while True:
            response = input('Indexes: ')
            if response == '':
               sys.exit()
            else:
               indexes = list(map(lambda x: x.strip(), response.split(',')))
               try:
                  indexes = list(map(lambda x: int(x), indexes))
               except ValueError:
                  click.echo('Try again.')
                  continue
               for index in indexes:
                  if index < 0 or index >= len(creds):
                     click.echo('Try again.')
                     break
               else:
                  break
         # Remove credentials
         credsToRemove = []
         indexes = sorted(list(set(indexes)))
         click.echo(indexes)
         for index in indexes:
            credsToRemove.append(creds[index])
         credentials.display(credsToRemove, 'Credentials to Remove', noPrimary=True)
         if click.confirm('Confirm?'):            
            credentials.delete(indexes)
            click.echo('Successfully removed.')
      else:
         click.echo('Nothing to remove.')
   else:
      click.echo('No saved credentials.')
