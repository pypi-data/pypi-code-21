import sys
import click
from halo import Halo
from icheckin import credentials, connections

@click.command('code', short_help='check-in with code')
@click.argument('checkincode')
@click.option('--multi', is_flag=True, help='Check-in multiple credentials.')
def command(checkincode, multi):
   # Check primary credentials
   primary = credentials.primary()
   if primary != ():
      click.echo('\nChecking in for:')
      for cred in credentials.read():
         spinner = Halo(text=cred[0])
         spinner.start()
         status = connections.checkin(cred, checkincode)
         if status == 0:
            spinner.succeed('%s - Successful' % cred[0])
         elif status == 1:
            spinner.fail('%s - No internet connection' % cred[0])
            sys.exit(0)
         elif status == 2:
            spinner.fail('%s - Invalid credentials' % cred[0])
         elif status == 3:
            spinner.fail('%s - Not connected to SunwayEdu Wi-Fi' % cred[0])
            sys.exit(0)
         elif status == 4:
            spinner.fail('%s - Invalid code' % cred[0])
            sys.exit(0)
         elif status == 5:
            spinner.fail('%s - Wrong class' % cred[0])
         elif status == 6:
            spinner.fail('%s - Already checked-in' % cred[0])
         if not multi:
            break
      click.echo('\nDone.')
   else:
      click.echo('Save primary credentials first before checking-in.')