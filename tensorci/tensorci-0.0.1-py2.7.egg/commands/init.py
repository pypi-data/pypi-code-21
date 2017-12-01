import os
import click
from tensorci import log, auth_required
from tensorci.utils import auth, gitconfig
from tensorci.proj_config.config_file import ConfigFile
from slugify import slugify


@click.command()
@click.option('--name', '-n')
def init(name):
  auth_required()

  curr_team = auth.get_team()

  if not curr_team:
    log("You must be actively using one of your teams before creating a new prediction.\n"
        "Use 'tensorci use-team NAME' to set a team as your current team.")
    return

  config = ConfigFile()

  if os.path.exists(config.path):
    log('Project already initialized.')
    return

  name = (name or click.prompt('Prediction Name')).strip()

  if not name:
    log('Prediction Name is required.')
    return

  git_repo, err = gitconfig.get_remote_url()

  if err:
    log(err)
    return

  name = slugify(name, separator='-', to_lower=True)

  config.set_value('name', name)
  config.set_value('repo', git_repo)
  config.set_value('model', 'path/to/model/file')
  config.set_value('create_dataset', 'module1.module2:function')
  config.set_value('train', 'module1.module2:function')
  config.set_value('test', 'module1.module2:function')
  config.set_value('predict', 'module1.module2:function')

  config.save()

  log('Initialized new TensorCI prediction: {}.\n\n'
      'Generated new config file at {}'.format(name, config.NAME))