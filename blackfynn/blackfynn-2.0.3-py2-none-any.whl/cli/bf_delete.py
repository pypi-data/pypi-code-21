'''
usage:
  bf delete [options] <item>

global options:
  -h --help                 Show help
  --profile=<name>          Use specified profile (instead of default)
'''

from docopt import docopt
from blackfynn import Dataset
from blackfynn.models import BaseNode

from cli_utils import get_client

def main():
    args = docopt(__doc__)

    bf = get_client()
    
    item = bf.get(args['<item>']) 
    if isinstance(item, Dataset):
        print "Error: cannot delete dataset"
        return
    elif not isinstance(item, BaseNode):
        print "Error: cannot delete item"
        return
    bf.delete(item)
