from . import yaml

from procgraph import simple_block


@simple_block
def yaml2object(s):
    return yaml.load(s)
