#!/usr/bin/env python
#
# Copyright 2012-2014 Ravello Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import, print_function

import os
from setuptools import setup


version_info = {
    'name': 'ravello-sdk',
    'version': '2.7',
    'description': 'Python SDK for the Ravello API',
    'author': 'Geert Jansen',
    'maintainer': 'Hadar Davidovich',
    'maintainer_email': 'hadar.davidovich@oracle.com',
    'url': 'https://github.com/ravello/python-sdk',
    'license': 'Apache 2.0',
    'classifiers': [
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ]
}

if __name__ == '__main__':
    setup(
        package_dir={'': 'lib'},
        py_modules=['ravello_sdk', 'ravello_cli'],
        install_requires=['six', 'docopt', 'requests>=2.6.0'],
        name= version_info['name'],
        version= version_info['version'],
        description= version_info['description'],
        author= version_info['author'],
        maintainer= version_info['maintainer'],
        maintainer_email= version_info['maintainer_email'],
        url= version_info['url'],
        license= version_info['license'],
        classifiers= version_info['classifiers']
    )
