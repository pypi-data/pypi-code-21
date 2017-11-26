

import sys,platform
from colorama import Fore, Back, Style
import click
from . import __version__

def get_version(ctx, param, value):
    print(Fore.GREEN )
    if not value or ctx.resilient_parsing:
        return
    message = 'Flask CLI :%(version)s\nPython :%(python_version)s \nOS:%(os)s'
    click.echo(message % {
        'version': __version__,
        'python_version': sys.version,
        'os':platform.system()+' ' + platform.release(),
        
    }, color=ctx.color)
    ctx.exit()

def new_flask_project(ctx, param, value):
    print(Fore.BLUE )
    if not value or ctx.resilient_parsing:
        return
    click.echo('creating new flask application:'+value)


@click.command()
@click.option('--verbose', is_flag=True, help="Will print verbose messages." )
@click.option('-v','--version', expose_value=False, callback=get_version, is_flag=True, is_eager=True,help='Show the flask cli version')
@click.option('-new','--new', expose_value=False, callback=new_flask_project,help='Create a new flask application')
def cli(verbose):
    if verbose:
        click.echo("We are in the verbose mode.")
    click.echo("success")






if __name__ == '__main__':

    print('hi')
