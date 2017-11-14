#!/usr/bin/env python
# -*- coding: utf-8 -*-

#!/usr/bin/env python

from os.path import exists
from setuptools import setup
import versioneer

ipython_req = 'ipython'

import sys
if sys.version_info[0] < 3 and 'bdist_wheel' not in sys.argv:
    ipython_req = 'ipython<6'

extras_require = {"tests": ["pytest"]}

extras_require['all'] = list(
    set([val for k, v in extras_require.items() for val in v]))

setup(
    name='smokey',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='smoke tests for nteract',
    author='nteract contributors',
    author_email='jupyter@googlegroups.com',
    license='BSD',
    keywords="smoke, jupyter, nteract",
    long_description=(open('README.md').read() if exists('README.md') else ''),
    url='https://github.com/nteract/smokey',
    packages=['smokey'],
    package_data={},
    install_requires=[ipython_req],
    extras_require=extras_require)
