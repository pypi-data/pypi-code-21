#!/usr/bin/python

from __future__ import print_function

"A distutils extension to freeze Python 3 scripts into Windows executables."

from setuptools import setup

import sys, os, re
from distutils.core import Command
from distutils.errors import DistutilsError
from distutils.extension import Extension
from os.path import abspath, dirname, exists, join
from distutils.util import get_platform

from build_exe import *


def main():
    minver = (3,6)
    if (sys.version_info.major, sys.version_info.minor) < minver:
        raise DistutilsError('Kelvin requires Python %s.%s or later' % minver)

    version = get_version()

    files = [ abspath(join('src', f)) for f in os.listdir('src') if f.endswith('.cpp') ]

    settings = { 'define_macros' : [('KELVIN_VERSION', version)],
                 'libraries' : ['Imagehlp', 'Shell32'] }

    # We need to set a build_lib since most of the distutils commands change it depending on
    # whether there are extensions or not.  We don't have extensions, but we do have
    # executables which should be treated the same.
    build_lib = join('build', 'lib.{}-{}'.format(get_platform(), sys.version[0:3]))
    exe_dir   = join(build_lib, 'kelvin', 'data')

    setup(
        distclass = Distribution2,
        name             = 'kelvin',
        version          = version,
        description      = 'Freezes Python scripts into Windows apps',
        long_description = __doc__,
        url              = 'http://www.gitlab.com/mkleehammer/kelvin',
        author           = 'Michael Kleehammer',
        author_email     = 'michael@kleehammer.com',

        packages    = ['kelvin'],

        exe_modules = [
            Executable('kelvinc', 'console', files, **settings),
            Executable('kelvinw', 'windows', files, **settings)
            ],

        options = { 'build'     : { 'build_lib': build_lib },
                    'build_exe' : { 'build_lib': exe_dir   },
                    'clean'     : { 'build_lib': build_lib },
                    'install'   : { 'build_lib': build_lib } },

        classifiers = ['Development Status :: 3 - Alpha',
                       'Intended Audience :: Developers',
                       'License :: OSI Approved :: MIT License',
                       'Operating System :: Microsoft :: Windows',
                       'Programming Language :: Python',
                       'Programming Language :: Python :: 3',
                       ],

        cmdclass = { 'build_exe': BuildExeCommand }
        )


def get_version():
    """
    Returns the version as a string.

    1. If in an unzipped source directory (from setup.py sdist), returns the version from the PKG-INFO file.
    2. If in a git repository, uses the latest tag from git describe.
    3. This should probably be an error, but it will return 0.1b1.
    """
    return _get_version_pkginfo() or _get_version_git() or '0.1b1'


def _get_version_pkginfo():
    filename = join(dirname(abspath(__file__)), 'PKG-INFO')
    if exists(filename):
        re_ver = re.compile(r'^Version: \s+ (\d.*)', re.VERBOSE)
        for line in open(filename):
            match = re_ver.search(line)
            if match:
                return match.group(1).strip()
    return None


def _get_version_git():
    n, result = getoutput('git describe --tags')
    if n:
        print('WARNING: git describe failed with: %s %s' % (n, result))
        return None

    match = re.match(r'(\d+).(\d+).(\d+)', result)
    if not match:
        return None

    major = int(match.group(1))
    minor = int(match.group(2))
    patch = int(match.group(3))

    modified = bool(getoutput('git --no-pager diff --quiet')[0]) # working directory
    if not modified:
        modified = bool(getoutput('git --no-pager diff --quiet --cached')[0]) # index

    version = '{}.{}.{}'.format(major, minor, patch)

    if modified:
        version += '.dev1'

    return version


def getoutput(cmd):
    pipe = os.popen(cmd, 'r')
    text   = pipe.read().rstrip('\n')
    status = pipe.close() or 0
    return status, text


if __name__ == '__main__':
    main()
