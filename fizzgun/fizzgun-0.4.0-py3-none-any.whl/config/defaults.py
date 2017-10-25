import yaml

from fizzgun.util import fizzgun_path


def defaults():
    with open(fizzgun_path('data', 'config_defaults.yaml'), 'r') as fh:
        return yaml.load(fh)
