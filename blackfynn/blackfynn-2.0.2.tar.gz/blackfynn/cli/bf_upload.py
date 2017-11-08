'''
usage:
  bf upload [options] [--to=destination] <file>...

global options:
  -h --help                 Show help
  --dataset=<dataset>       Use specified dataset (instead of your current working dataset)
  --profile=<name>          Use specified profile (instead of default)
'''

from docopt import docopt
from blackfynn import settings
from cli_utils import recursively_upload, get_client
import os

def main():
    args = docopt(__doc__)

    bf = get_client()

    files = args['<file>']

    if args['--to']:
        collection = bf.get(args['destination'])
        recursively_upload(bf, collection, files)

    elif settings.working_dataset:
        dataset = bf.get_dataset(settings.working_dataset)
        recursively_upload(bf, dataset, files)
