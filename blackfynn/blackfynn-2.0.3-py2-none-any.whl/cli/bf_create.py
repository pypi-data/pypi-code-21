'''
usage:
  bf create [options] (dataset | ds)   <name>
  bf create [options] (collection | c) <name> <destination>

global options:
  -h --help                 Show help
  --profile=<name>          Use specified profile (instead of default)
'''
from docopt import docopt
from blackfynn import Collection

from cli_utils import get_client

def main():
    args = docopt(__doc__)

    bf = get_client()
    
    if args['collection'] or args['c']:
        dest = args['<destination>']
        name = args['<name>']
        c = Collection(name)
        parent = bf.get(dest)
        parent.add(c)
        print(c)
    elif args['dataset'] or args['ds']:
        name = args['<name>']
        ds = bf.create_dataset(name)
        print ds
