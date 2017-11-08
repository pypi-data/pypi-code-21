'''
usage:
  bf upload [options] <destination> <file>...

global options:
  -h --help                 Show help
  --profile=<name>          Use specified profile (instead of default)
'''

from docopt import docopt
from cli_utils import recursively_upload, get_client
import os

def main():
    args = docopt(__doc__)

    bf = get_client()
    
    files = args['<file>']
    dest  = args['<destination>']
    recursively_upload(bf,dest,files)
