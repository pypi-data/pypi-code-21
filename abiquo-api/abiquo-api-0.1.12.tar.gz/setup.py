# Copyright (C) 2008 Abiquo Holdings S.L.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
from setuptools import setup

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    read_md = lambda f: open(f, 'r').read()

version_regex = r'__version__ = ["\']([^"\']*)["\']'
with open('abiquo/__init__.py', 'r') as f:
    text = f.read()
    match = re.search(version_regex, text)
    if match:
        VERSION = match.group(1)
    else:
        raise RuntimeError("No version number found!")

setup(
    name='abiquo-api',
    version=VERSION,
    description='Abiquo API Python Client',
    long_description=read_md('README.md'),
    author='Abiquo',
    author_email='developers@abiquo.com',
    url='https://github.com/abiquo/api-python-client',
    packages=['abiquo'],
    license='Apache License 2.0',
    keywords='abiquo api rest',
    install_requires=[
        'requests >= 2.0.0',
        'requests_oauthlib >= 0.4.2'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ]
)
