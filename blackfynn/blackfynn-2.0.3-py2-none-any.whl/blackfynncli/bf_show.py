'''Show an item, list datasets, or orgs

usage:
  bf show [options] (datasets | ds)
  bf show [options] orgs
  bf show [options] <item>

global options:
  -h --help                 Show help
  --profile=<name>          Use specified profile (instead of default)
'''

from docopt import docopt

from cli_utils import get_client

def main():
    args = docopt(__doc__)

    bf = get_client()

    if args['datasets'] or args['ds']:
        print "Datasets:"
        for ds in bf.datasets():
            print " * {} (id: {})".format(ds.name, ds.id)
    elif args['orgs']:
        print('Organizations:')
        for o in bf.organizations():
            print " * {} (id: {})".format(o.name, o.id)
    elif args['<item>'][:2] == 'N:':
        try:
            item = bf.get(args['<item>'])
            print item
            if hasattr(item, 'items'):
                print "CONTENTS:"
                for i in item.items:
                    print " * {}".format(i)
            if hasattr(item, 'channels'):
                print "CHANNELS:"
                for ch in item.channels:
                    print " * {} (id: {})".format(ch.name, ch.id)
        except:
            print("Invalid item: '{}'".format(args['<item>']))
