'''
    ModernGL extensions
'''

# pylint: disable=unused-argument, too-few-public-methods, no-self-use

import os
import sys


class ExtensionFinder():
    '''
        ExtensionFinder
    '''

    def find_spec(self, fullname, path, target=None):
        '''
            find_spec
        '''

        prefix = 'ModernGL.ext.'

        if fullname.startswith(prefix):
            name = fullname[len(prefix):]
            if '.' in name:
                return

            here = os.path.dirname(__file__)
            path = os.path.join(here, name)

            if not os.path.isdir(path):
                local = os.path.isfile(os.path.join(here, 'README.md'))

                if local:
                    error = 'missing extension\n\nDo not run ModernGL from the git repository!\n\n'
                    error += 'For developers:\n'
                    error += '\tpython -m pip install %s\n' % fullname
                    error += '\tpython -m ModernGL.ext --collect'

                else:
                    error = 'missing extension\n\nHint: python -m pip install %s' % fullname

                raise ModuleNotFoundError(error)


sys.meta_path.append(ExtensionFinder())
