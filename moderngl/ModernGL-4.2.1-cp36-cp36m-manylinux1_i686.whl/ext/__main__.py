'''
    ModernGL extensions main
'''

import argparse
import os
import sys
import shutil


def main(argv=None):
    '''
        main
    '''

    parser = argparse.ArgumentParser(prog='ModernGL.ext')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--list', action='store_true', help='list extensions')
    group.add_argument('--collect', action='store_true', help='collect extensions')
    args = parser.parse_args(argv)

    here = os.path.dirname(__file__)

    if args.list:
        for folder in os.listdir(here):
            if folder == '__pycache__' or not os.path.isdir(os.path.join(here, folder)):
                continue

            print('ModernGL.ext.' + folder)

    if args.collect:
        if not os.path.isfile(os.path.join(here, 'README.md')):
            print('Cannot collect extensions for the installed version of ModernGL.')
            exit()

        for path in sys.path:
            ext = os.path.normpath(os.path.join(path, 'ModernGL', 'ext'))
            if not os.path.isdir(ext):
                continue

            for folder in os.listdir(ext):
                found_ext = os.path.join(ext, folder)
                local_ext = os.path.join(here, folder)

                if folder == '__pycache__' or not os.path.isdir(found_ext) or os.path.isdir(local_ext):
                    continue

                shutil.copytree(found_ext, local_ext, ignore=lambda src, names: {'__pycache__'})
                print('copied "%s" to "%s"' % (found_ext, local_ext))

    if not args.list and not args.collect:
        parser.print_help()


if __name__ == '__main__':
    main()
