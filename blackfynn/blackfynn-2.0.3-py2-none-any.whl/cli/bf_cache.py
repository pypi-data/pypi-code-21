'''
usage:
  bf cache [options] clear
  bf cache [options] compact

global options:
  -h --help                 Show help
  --profile=<name>          Use specified profile (instead of default)
'''

from docopt import docopt

def main():
    args = docopt(__doc__)

    from blackfynn.cache import cache

    if args['clear']:
        print "Clearing cache...",
        cache.clear()
        print "done."
    elif args['compact']:
        cache.start_compaction(async=False)
