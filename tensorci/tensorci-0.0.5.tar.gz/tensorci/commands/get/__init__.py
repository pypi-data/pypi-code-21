import click
from model import model


@click.group()
def get():
  pass

get.add_command(model)