import click

from .function import function


@click.group()
def new():
    pass


new.add_command(function)
