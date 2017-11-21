#!/usr/bin/env python

import os
import re
import sys

from setuptools import find_packages
from setuptools import setup

NAME =               'ipyk'
VERSION =            '0.1.4.2'
AUTHOR =             'Lev Givon'
AUTHOR_EMAIL =       'lev@columbia.edu'
URL =                'https://github.com/lebedov/ipyk/'
DESCRIPTION =        'IPython local kernel management utility'
with open('README.rst', 'r') as f:
    LONG_DESCRIPTION = f.read()
LONG_DESCRIPTION = re.search('.*(^Package Description.*)', LONG_DESCRIPTION, re.MULTILINE|re.DOTALL).group(1)
DOWNLOAD_URL =       URL
LICENSE =            'BSD'
CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Framework :: IPython',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3',
    'Topic :: Software Development']

if __name__ == "__main__":
    if os.path.exists('MANIFEST'):
        os.remove('MANIFEST')

    install_requires = ['ipython>=4.0.0',
                        'ipykernel>=4.0.0',
                        'jupyter_client>=4.0.0',
                        'jupyter_core>=4.0.0',
                        'setproctitle',
                        'six']
    if sys.version_info < (3, 0):
        install_requires += ['futures>=3.0']
    setup(
        name = NAME,
        version = VERSION,
        author = AUTHOR,
        author_email = AUTHOR_EMAIL,
        license = LICENSE,
        classifiers = CLASSIFIERS,
        description = DESCRIPTION,
        long_description = LONG_DESCRIPTION,
        url = URL,
        scripts = ['ipyk'],
        install_requires = install_requires
    )
