import os

import click
import jinja2

from new import new
from pack import pack


@click.group()
def apex_cli():
    pass


apex_cli.add_command(new)
apex_cli.add_command(pack)


if __name__ == '__main__':
    apex_cli()
