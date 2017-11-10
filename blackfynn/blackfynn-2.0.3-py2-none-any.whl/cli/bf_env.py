'''
usage:
  bf env [options]

global options:
  -h --help                 Show help
  --profile=<name>          Use specified profile (instead of default)
'''
from docopt import docopt

from blackfynn import settings

from cli_utils import get_client

def main():
    args = docopt(__doc__)

    print('Active profile:\n  \033[32m{}\033[0m\n'.format(settings.active_profile))

    if len(settings.eVars.keys()) > 0:
        key_len = 0
        value_len = 0
        for key, value in settings.eVars.items():
            key_len = max(key_len,len(key))
            value_len = max(value_len,len(value[0]))
        
        print('Environment variables:')
        print('  \033[4m{:{key_len}}    {:{value_len}}    {}'.format('Key','Value','Environment Variable\033[0m',key_len=key_len,value_len=value_len))
        for key, value in sorted(settings.eVars.items()):
           print('  {:{key_len}}    {:{value_len}}    {}'.format(key,value[0],value[1],key_len=key_len,value_len=value_len))
        print
           
    bf = get_client()
    
    print "Blackfynn environment:"
    print "  User          : {}".format(bf.profile.email)
    print "  Organization  : {} (id: {})".format(bf.context.name, bf.context.id)
    print "  API Location  : {}".format(bf.host)
    print "  Streaming API : {}".format(settings.streaming_api_host)
