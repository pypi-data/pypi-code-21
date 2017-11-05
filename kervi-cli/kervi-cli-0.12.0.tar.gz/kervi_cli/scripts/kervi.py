import click
from .commands.create import create

@click.group()
def cli():
    pass

cli.add_command(create)
#entry_point.add_command(group2.version)    