import click
from icheckin.commands import *
from icheckin.commands import MODULES

@click.group()
def cli():
   pass

# Add all commands to cli
for module in MODULES:
	cli.add_command(getattr(locals()[module], 'command'))
   
if __name__ == '__main__':
	cli()