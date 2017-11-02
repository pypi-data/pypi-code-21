import sys
import click
from icheckin import credentials

@click.command('add', short_help='add to existing credentials')
def command():
   # Check primary credentials
   if credentials.primary() != ():
      # Display credentials
      creds = credentials.read()
      credentials.display(creds, 'Existing Credentials')
      # Prompt to add
      count = len(creds)
      creds = []
      if count != credentials.maximum():
         click.echo('[Enter twice to stop adding]')  
         while True:
            cred = credentials.prompt()
            if cred == ('', ''):
               break
            else:
               if '' not in cred:
                  creds.append(cred)
                  count += 1
                  # Check max
                  if count != credentials.maximum():
                     click.echo('[Next]')
                  else:
                     click.echo('[Maximum credentials reached: %s]' % 
                        str(credentials.maximum()))
                     break
               else:
                  click.echo('Try again.')
      else:
         click.echo('Maximum credentials already.')
         sys.exit(0)
      # Confirm
      if len(creds) != 0:
         credentials.display(creds, 'Credentials to Add', noPrimary=True)
         if click.confirm('Confirm?'):
            credentials.append(creds)
            click.echo('Successfully added.')
         else:
            click.echo('Cancelled.')
   else:
      click.echo('Save primary credentials first before adding.')