import os
import yaml

from bash import marshal_dict_to_bash_env

CONFIG_DIR = os.path.expanduser('~/.config/blunix')
DEFAULT_CONFIG = 'blunix.yaml'
DEFAULT_CONFIG_CONTENT = """# vim: set ft=yaml ts=2 sw=2 si

# This is the main Blunix configuration file for every engineer.
# It is located at ~/.config/blunix/blunix.yaml

version: 0.1.3
devop:
  name: ""
  last: ""
  nick: ""
  mail: ""
github:
  user: ""
  pass: ""  # use an access token: https://github.com/settings/tokens
  org: blunix
root_dir:
  workspace: ~/src/github.com/blunix

"""


def config_file():
    return os.path.join(CONFIG_DIR, DEFAULT_CONFIG)


def get():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR, 0o775)

    if not os.path.exists(config_file()):
        with open(config_file(), 'w') as cf:
            cf.write(DEFAULT_CONFIG_CONTENT)
            cf.flush()
        edit()

    with open(config_file(), 'r') as fd:
        return yaml.load(fd)


def edit():
    editor = os.getenv('EDITOR', 'vi')
    os.system('{} "{}"'.format(editor, config_file()))
