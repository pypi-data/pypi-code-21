'''usage:
  bf [options] [<command>] [<args>...]

Available commands:
  append        Append data to a datset
  cache         Perform cache operations
  create        Create dataset or collection
  dataset       Dataset actions
  delete        Delete item
  env           Display bf environment
  path          Show path to item
  profile       Profile management
  upload        Upload file(s) or directory
  search        Search datasets
  show          Show datasets, orgs, or contents of an item

global options:
  -h --help                 Show help
  --profile=<name>          Use specified profile (instead of default)
'''

from docopt import docopt
import os


def main():
    """
    Primary entrypoint to Blackfynn CLI
    """
    from blackfynn.version import version
    args = docopt(__doc__,
                  version='bf version {}'.format(version),
                  options_first=True)

    #Display warning message if config.ini is not found
    from blackfynn import settings
    if args['<command>'] != 'profile':
        if not os.path.exists(settings.config_file):
            print("\033[31m* Warning: No config file found, run 'bf profile' to start the setup assistant\033[0m")

    #Try to use profile specified by --profile, exit if invalid
    try:
        if args['--profile'] is not None:
            settings.use_profile(args['--profile'])
    except Exception, e:
        exit(e)
        
    if args['<command>'] == 'env':
        import bf_env
        bf_env.main()
    elif args['<command>'] == 'cache':
        import bf_cache
        bf_cache.main()
    elif args['<command>'] == 'create':
        import bf_create
        bf_create.main()
    elif args['<command>'] == 'delete':
        import bf_delete
        bf_delete.main()
    elif args['<command>'] == 'show':
        import bf_show
        bf_show.main()
    elif args['<command>'] == 'path':
        import bf_path
        bf_path.main()        
    elif args['<command>'] == 'upload':
        import bf_upload
        bf_upload.main()
    elif args['<command>'] == 'append':
        import bf_append
        bf_append.main()
    elif args['<command>'] == 'search':
        import bf_search
        bf_search.main()
    elif args['<command>'] == 'dataset':
        import bf_dataset
        bf_dataset.main()
    elif args['<command>'] == 'profile':
        import bf_profile
        bf_profile.main()
    elif args['<command>'] in ['help',None]:
        print(__doc__.strip('\n'))
        return
    else:
        exit("Invalid command: '{}'\nSee 'bf help' for available commands".format(args['<command>']))
