import git
import os


def get_remote_url(remote='origin'):
  git_path = '{}/.git'.format(os.getcwd())
  is_git_repo = os.path.exists(git_path) and os.path.isdir(git_path)

  if not is_git_repo:
    return None, 'Current project is not a git repository.'

  config_path = '{}/config'.format(git_path)

  if not os.path.exists(config_path):
    return None, '.git/config file missing...'

  try:
    config = git.GitConfigParser([config_path], read_only=True)
  except BaseException:
    return None, 'Error parsing .git/config file...'

  try:
    url = config.get_value('remote "{}"'.format(remote), 'url')
  except BaseException:
    return None, 'Error determining remote origin url...make sure you have a git remote origin set up.'

  return str(url), None