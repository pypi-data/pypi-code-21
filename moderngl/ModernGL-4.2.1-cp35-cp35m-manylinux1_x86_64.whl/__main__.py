'''
    ModernGL main
'''

import argparse
import json
import os
import sys

import ModernGL


def main(argv=None):
    '''
        main
    '''

    parser = argparse.ArgumentParser(prog='ModernGL')
    parser.add_argument('-v', '--version', action='version', version='ModernGL %s' % ModernGL.__version__)
    parser.add_argument('-i', '--info', action='store_true', default=False)
    args = parser.parse_args(argv)

    ctx = ModernGL.create_standalone_context()

    if args.info:
        print(json.dumps(ctx.info, sort_keys=True, indent=4))

    else:
        repo = os.path.isfile(os.path.join(os.path.dirname(__file__), 'README.md'))
        install = '(git repository)' if repo else '(installed)'

        print('ModernGL:', ModernGL.__version__, install)
        print('Vendor:', ctx.vendor)
        print('Renderer:', ctx.renderer)
        print('Version:', ctx.version)
        print('Python:', sys.version)
        print('Platform:', sys.platform)


if __name__ == '__main__':
    main()
