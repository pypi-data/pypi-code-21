'''
usage:
  bf path [options] <item>

global options:
  -h --help                 Show help
  --profile=<name>          Use specified profile (instead of default)
'''

from docopt import docopt
from cli_utils import print_path_tree, get_client
        
def main():
    args = docopt(__doc__)

    bf = get_client()
    
    item = bf.get(args['<item>'])
    print_path_tree(bf, [item])
