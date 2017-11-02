import sys
import click
from icheckin import credentials

@click.command('save', short_help='save new credentials')
def command():
   # Display existing credentials
   question = 'Save new credentials?'
   message = 'Successfully saved.'
   if credentials.exist():
      question = 'Overwrite credentials?'
      message = 'Successfully overwritten.'
      creds = credentials.read()
      credentials.display(creds, 'Existing Credentials')
         
   # Save credentials
   if click.confirm(question):
      creds = []
      # Primary credentials
      click.echo('\n[Enter twice to exit]')
      while True:
         cred = credentials.prompt('Primary student id',
            'Primary password')
         if cred == ('', ''):
            sys.exit(0)
         else:
            if '' not in cred:
               creds.append(cred)
               break
            else:
               click.echo('Try again.')      
      # Secondary credentials
      if click.confirm('\nAdd more credentials?'):
         click.echo('\n[Enter twice to stop adding]')
         while True:
            cred = credentials.prompt()
            if cred == ('', ''):
               break
            else:
               if '' not in cred:
                  creds.append(cred)
                  # Check max
                  if len(creds) != credentials.maximum():
                     click.echo('[Next]')
                  else:
                     click.echo('[Maximum credentials reached: %s]' % 
                        str(credentials.maximum()))
                     break
               else:
                  click.echo('Try again.')
      # Confirm
      credentials.display(creds, 'New Credentials')
      if click.confirm('Confirm?'):
         credentials.write(creds)
         click.echo(message)
      else:
         click.echo('Cancelled.')

