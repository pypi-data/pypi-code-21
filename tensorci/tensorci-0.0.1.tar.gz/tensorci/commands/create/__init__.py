import click
from team import team


@click.group()
def create():
  pass

create.add_command(team)