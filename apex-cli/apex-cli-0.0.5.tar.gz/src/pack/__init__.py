import click

from .install import install


@click.group()
def pack():
    pass


pack.add_command(install)
