import click
from tensorci import log, auth_required
from tensorci.utils import auth
from slugify import slugify
from tensorci.utils.api import api, ApiException


@click.command(name='use-team')
@click.argument('name')
def use_team(name):
  """
  Switches current team to desired team by nasme.

  :param team: str (required)
  :return: None
  """
  auth_required()

  team_slug = slugify(name, separator='-', to_lower=True)

  try:
    resp = api.get('/teams')
    teams = resp.get('data')
  except ApiException as e:
    log(e.message)
    return

  if not teams:
    log("You currently don't have any TensorCI teams to use.\n"
        "You can create one with 'tensorci create team NAME'.")
    return

  team_slugs = [t.get('slug') for t in teams]

  if team_slug not in team_slugs:
    log("You currently don't have a team named '{}'.".format(team_slug))
    return

  auth.set_team(team_slug)

  log('Set current team to {}.'.format(name))