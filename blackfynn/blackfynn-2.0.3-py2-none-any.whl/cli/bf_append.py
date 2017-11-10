'''
usage:
  bf append [options] <destination> <file>...

global options:
  -h --help                 Show help
  --profile=<name>          Use specified profile (instead of default)
'''

from docopt import docopt

from cli_utils import get_client

def main():
    args = docopt(__doc__)

    bf = get_client()
    
    files = args['<file>']
    dest  = args['<destination>']
    bf._api.io.upload_files(dest, files, append=True, display_progress=True)
