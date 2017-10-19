#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    Meng xiangguo <mxgnene01@gmail.com>
#
#              _____               ______
#     ____====  ]OO|_n_n__][.      |    |]
#    [________]_|__|________)<     |MENG|
#     oo    oo  'oo OOOO-| oo\_   ~o~~~o~'
# +--+--+--+--+--+--+--+--+--+--+--+--+--+
#                        2017/10/18  下午7:13

import os
import sys
import setuptools
from version import __VERSION__

def _setup():
    setuptools.setup(
        name='itester',
        version=__VERSION__,
        description='Excel - driven interface automation framework',
        author='Xiangguo Meng',
        author_email='mxgnene01@gmail.com',
        install_requires=['requests', 'click', 'xlrd'],
        packages=['itester'],
        license='LICENSE',
        url='https://github.com/mxgnene01/itester',
        include_package_data=True,
        long_description=open('README.md').read(),
        entry_points={
            'console_scripts': [
                'itester=itester.itester:main',
                ]
            }
    )

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == 'publish':
            os.system('make publish')
            sys.exit()
        elif sys.argv[1] == 'release':
            if len(sys.argv) < 3:
                type_ = 'patch'
            else:
                type_ = sys.argv[2]
            assert type_ in ('major', 'minor', 'patch')

            os.system('bumpversion --current-version {} {}'
                      .format(__VERSION__, type_))
            sys.exit()

    _setup()


if __name__ == '__main__':
    main()
