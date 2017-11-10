'''
usage:
  bf dataset [options] <dataset> [<command>] [<action>] [<action-args>...]

global options:
  -h --help                 Show help
  --profile=<name>          Use specified profile (instead of default)
'''

from docopt import docopt
import sys

from cli_utils import get_client

def main():
    args = docopt(__doc__)

    bf = get_client()
    
    ds = bf.get(args['<dataset>'])
    if args['collaborators']:
        if args['<action>'] == 'ls':
            resp = ds.collaborators()
            print " - Users"
            for u in resp['users']:
                print "   - email:{} id:{}".format(u.email, u.id)
            print " - Groups"
            for g in resp['groups']:
                print "   - name:{} id:{}".format(g.name, g.id)
        elif args['<action>'] == 'add':
            ids = args['<action-args>']
            if len(ids) == 0:
                print "Error: No ids specified"
                sys.exit(1)
            resp = ds.add_collaborators(*ids)
            print_collaborator_edit_resp(resp)
        elif args['<action>'] == 'rm':
            ids = args['<action-args>']
            if len(ids) == 0:
                print "Error: No ids specified"
                sys.exit(1)
            resp = ds.remove_collaborators(*ids)
            print_collaborator_edit_resp(resp)
        else:
            print "Error: invalid dataset collaborators command. Valid commands are 'ls', 'add' or 'rm'"

    
