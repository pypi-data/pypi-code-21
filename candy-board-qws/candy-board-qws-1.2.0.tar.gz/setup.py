#!/usr/bin/env python

# Copyright (c) 2017 CANDY LINE INC.
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

import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

version = "1.2.0"

try:
    import pypandoc
    readme_txt = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    readme_txt = ""


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


if sys.argv[-1] == 'publish':
    os.system('rm -fr dist/*')
    os.system('python setup.py sdist')
    os.system('twine upload dist/*')
    sys.exit()

setup(
    name='candy-board-qws',
    version=version,
    author='Daisuke Baba',
    author_email='baba.daisuke@gmail.com',
    url='http://github.com/CANDY-LINE/candy-board-qws',
    download_url='https://github.com/CANDY-LINE/candy-board-qws/tarball/{0}'
                 .format(version),
    description='Base CANDY LINE boards service for '
        'Quectel Wireless Solutions Modules',
    long_description=readme_txt,
    packages=find_packages('lib'),
    package_dir={'': 'lib'},
    license='ASL 2.0',
    classifiers=[
                    'Programming Language :: Python',
                    'Development Status :: 5 - Production/Stable',
                    'Natural Language :: English',
                    'Environment :: Console',
                    'Intended Audience :: System Administrators',
                    'Intended Audience :: Developers',
                    'License :: OSI Approved :: Apache Software License',
                    'Operating System :: POSIX :: Linux',
                    'Topic :: System :: Hardware',
                 ],
    keywords=('CANDY RED', 'CANDY EGG', 'CANDY LINE'),
    tests_require=['pytest-cov>=2.2.0',
                   'pytest>=2.6.4',
                   'terminaltables>=1.2.1'],
    cmdclass={'test': PyTest}
)
