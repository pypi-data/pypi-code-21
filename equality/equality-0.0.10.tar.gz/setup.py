#!/usr/bin/env python
from glob import glob
import os
from os.path import join
import re

from setuptools import setup, find_packages

# DON'T IMPORT non-stdlib modules, other than setuptools, at module level,
# since this requires them to be installed to run any setup.py command. (e.g.
# 'setup.py install' should not require installing py2exe.)

# DON'T IMPORT from our local source, since pip needs to be able to import
# setup.py before our dependencies have been installed.

NAME = 'equality'

# This lib's dependencies:
INSTALL_REQUIRES = [
]

def read_description(filename):
    '''
    Read given textfile and return (3rd_para, 4th to final paras)
    '''
    with open(filename) as fp:
        text = fp.read()
    paras = text.split('\n\n')
    return paras[1], '\n\n'.join(paras[2:])

def read_file(filename):
    with open(filename, "rt") as filehandle:
        return filehandle.read()

def find_value(source, identifier):
    '''
    Manually parse the given source, looking for lines of the form:
        <identifier> = '<value>'
    Returns the value. We do this rather than import the file directly because
    its dependencies will not be present when setuptools runs this setup.py
    before installing our dependencies, to find out what they are.
    '''
    regex =r"^%s\s*=\s*['\"]([^'\"]*)['\"]$" % (identifier,)
    match = re.search(regex, source, re.M)
    if not match:
        raise RuntimeError(
            "Can't find '%s' in source:\n%s" % (identifier, source)
        )
    return match.group(1)

def get_sdist_config():
    description, long_description = read_description('README.rst')

    return dict(
        name=NAME,
        version=find_value(read_file(join(NAME, '__init__.py')), '__version__'),
        description=description,
        long_description=long_description,
        url='http://pypi.python.org/pypi/%s/' % (NAME,),
        author='Jonathan Hartley',
        author_email='tartley@tartley.com',
        keywords='test testing equal equals equality',
        install_requires=INSTALL_REQUIRES,
        packages=find_packages(exclude=['*.tests']),
        # see classifiers:
        # http://pypi.python.org/pypi?:action=list_classifiers
        classifiers=[
            #'Development Status :: 1 - Planning',
            'Development Status :: 2 - Pre-Alpha',
            #'Development Status :: 3 - Alpha',
            #'Development Status :: 4 - Beta',
            #'Development Status :: 5 - Production/Stable',
            #'Development Status :: 6 - Mature',
            #'Development Status :: 7 - Inactive',
            'Environment :: Console',
            #'Environment :: MacOS X',
            #'Environment :: No Input/Output (Daemon)',
            #'Environment :: Web Environment',
            #'Environment :: Win32 (MS Windows)',
            #'Environment :: X11 Applications',
            'Intended Audience :: Developers',
            #'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: BSD License',
            'Natural Language :: English',
            'Operating System :: Microsoft :: Windows :: Windows 7',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: POSIX :: Linux',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: Implementation :: CPython',
        ],
        zip_safe=True,
    )

def main():
    setup(**get_sdist_config())

if __name__ == '__main__':
    main()

