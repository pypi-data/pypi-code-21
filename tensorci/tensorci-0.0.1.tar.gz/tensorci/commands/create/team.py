import click
from tensorci import log, auth_required
from tensorci.utils import auth
from tensorci.utils.api import api, ApiException
from slugify import slugify


@click.command()
@click.argument('name')
def team(name):
  """
  Create TensorCI team with a unique name.
  Switches current team to this new team upon successful creation.

  :param name: str (required)
  :return: None
  """
  auth_required()

  try:
    api.post('/team', payload={'name': name})
  except ApiException as e:
    log(e.message)
    return

  log('Successfully created team {}.'.format(name))

  team_slug = slugify(name, separator='-', to_lower=True)
  auth.set_team(team_slug)

  log('Set current team to {}.'.format(name))