#!/usr/bin/env python

# This file is part of tako
# Copyright (c) 2015-2017 Adam Hartz <hartz@mit.edu> and contributors
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# tako is a fork of xonsh (http://xon.sh)
# xonsh is Copyright (c) 2015-2016 the xonsh developers and is licensed under
# the 2-Clause BSD license.

# -*- coding: ascii -*-
"""The tako installer."""
from __future__ import print_function, unicode_literals
import os
import sys
import json

try:
    from tempfile import TemporaryDirectory
except ImportError:
    pass

try:
    from setuptools import setup
    from setuptools.command.sdist import sdist
    from setuptools.command.install import install
    from setuptools.command.develop import develop
    from setuptools.command.install_scripts import install_scripts
    HAVE_SETUPTOOLS = True
except ImportError:
    from distutils.core import setup
    from distutils.command.sdist import sdist as sdist
    from distutils.command.install import install as install
    from distutils.command.install_scripts import install_scripts
    HAVE_SETUPTOOLS = False

from takoshell import __version__ as TAKO_VERSION

TABLES = ['takoshell/lexer_table.py', 'takoshell/parser_table.py']


def clean_tables():
    """Remove the lexer/parser modules that are dynamically created."""
    for f in TABLES:
        if os.path.isfile(f):
            os.remove(f)
            print('Remove ' + f)


def build_tables():
    """Build the lexer/parser modules."""
    print('Building lexer and parser tables.')
    sys.path.insert(0, os.path.dirname(__file__))
    from takoshell.parser import Parser
    Parser(lexer_table='lexer_table', yacc_table='parser_table',
           outputdir='takoshell')
    sys.path.pop(0)


class xinstall(install):
    """Xonsh specialization of setuptools install class."""
    def run(self):
        clean_tables()
        build_tables()
        install.run(self)


class xsdist(sdist):
    """Xonsh specialization of setuptools sdist class."""
    def make_release_tree(self, basedir, files):
        clean_tables()
        build_tables()
        sdist.make_release_tree(self, basedir, files)


#-----------------------------------------------------------------------------
# Hack to overcome pip/setuptools problem on Win 10.  See:
#   https://github.com/tomduck/pandoc-eqnos/issues/6
#   https://github.com/pypa/pip/issues/2783

# Custom install_scripts command class for setup()
class install_scripts_quoted_shebang(install_scripts):
    """Ensure there are quotes around shebang paths with spaces."""
    def write_script(self, script_name, contents, mode="t", *ignored):
        shebang = str(contents.splitlines()[0])
        if shebang.startswith('#!') and ' ' in shebang[2:].strip() \
          and '"' not in shebang:
            quoted_shebang = '#!"%s"' % shebang[2:].strip()
            contents = contents.replace(shebang, quoted_shebang)
        super().write_script(script_name, contents, mode, *ignored)

# The custom install needs to be used on Windows machines
if os.name == 'nt':
    cmdclass = {'install': xinstall, 'sdist': xsdist, 'install_scripts': install_scripts_quoted_shebang}
else:
    cmdclass = {'install': xinstall, 'sdist': xsdist}


if HAVE_SETUPTOOLS:
    class xdevelop(develop):
        """Xonsh specialization of setuptools develop class."""
        def run(self):
            clean_tables()
            build_tables()
            develop.run(self)


def main():
    """The main entry point."""
    if sys.version_info[:2] < (3, 4):
        sys.exit('tako currently requires Python 3.4+')
    if '--name' not in sys.argv:
        print(' ____ \n( oo )\n_||||_\n      \n TAKO \n')
    skw = dict(
        name='takoshell',
        description='Pythonic shell language and command prompt',
        long_description='tako is a Pythonic shell language and command prompt. https://takoshell.org',
        license='GPLv3+',
        version=TAKO_VERSION,
        author='Adam Hartz',
        maintainer='Adam Hartz',
        author_email='hartz@mit.edu',
        url='https://takoshell.org',
        platforms='Cross Platform',
        classifiers=['Development Status :: 4 - Beta',
                     'Environment :: Console',
                     'Intended Audience :: Developers',
                     'Intended Audience :: End Users/Desktop',
                     'Natural Language :: English',
                     'Operating System :: POSIX',
                     'Programming Language :: Python :: 3 :: Only',
                     'Topic :: System :: Shells',
                     'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)'],
        packages=['takoshell', 'takoshell.ply', 'takoshell.parsers',
                  'takoshell.coreutils', 'takoshell.completers'],
        package_dir={'takoshell': 'takoshell'},
        package_data={'takoshell': ['*.json', 'LICENSE']},
        cmdclass=cmdclass
        )
    if HAVE_SETUPTOOLS:
        skw['entry_points'] = {
            'console_scripts': ['tako = takoshell.main:main'],
            }
        skw['cmdclass']['develop'] = xdevelop
        skw['install_requires'] = []
    else:
        skw['scripts'] = ['scripts/tako']

    setup(**skw)


if __name__ == '__main__':
    main()
