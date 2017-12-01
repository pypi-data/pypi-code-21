import click
from tensorci import log
from tensorci.utils import auth


@click.command()
def logout():
  """
  Logs a TensorCI user out of the CLI.
  Removes CLI api host from netrc.

  :return: None
  """
  auth.delete()
  log('Successfully logged out.')