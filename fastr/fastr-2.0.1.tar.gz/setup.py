# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
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

import imp
import os
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

with open('requirements.txt', 'r') as fh:
    _requires = fh.read().splitlines()

with open('test_requirements.txt', 'r') as fh:
    _tests_require = fh.read().splitlines()

with open('README', 'r') as fh:
    _description = fh.read()


def scan_dir(path, prefix=None):
    if prefix is None:
        prefix = path

    # Scan resources package for files to include
    file_list = []
    for root, dirs, files in os.walk(path):
        # Strip this part as setup wants relative directories
        root = root.replace(prefix, '')
        root = root.lstrip('/\\')

        for filename in files:
            if filename[0:8] == '__init__':
                continue
            file_list.append(os.path.join(root, filename))

    return file_list

# Create version file
version = imp.load_source('version', os.path.join(os.path.dirname(__file__), 'fastr', 'version.py'))
__version__ = version.version
version.save_version(__version__, version.hg_head, version.hg_branch)

# Determine the extra resources and scripts to pack
resources_list = scan_dir('./fastr/resources')
examples_list = scan_dir('./fastr/examples/data', './fastr/examples')
web_list = scan_dir('./fastr/web/static', './fastr/web')
web_list += scan_dir('./fastr/web/templates', './fastr/web')

print('[setup.py] called with: {}'.format(' '.join(sys.argv)))
if hasattr(sys, 'real_prefix'):
    print('[setup.py] Installing in virtual env {} (real prefix: {})'.format(sys.prefix, sys.real_prefix))
else:
    print('[setup.py] Not inside a virtual env!')


class NoseTestCommand(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # Run nose ensuring that argv simulates running nosetests directly
        import nose
        nose.run_exit(argv=['nosetests'])

# Set the entry point
entry_points = {
    "console_scripts": [
        "fastr = fastr.utils.cmd.__init__:main",
    ]
}

setup(
    name='fastr',
    version=__version__,
    author='H.C. Achterberg, M. Koek',
    author_email='hakim.achterberg@gmail.com',
    packages=['fastr',
              'fastr.core',
              'fastr.core.test',
              'fastr.data',
              'fastr.examples',
              'fastr.examples.test',
              'fastr.execution',
              'fastr.resources',
              'fastr.utils',
              'fastr.utils.cmd',
              'fastr.web'],
    package_data={'fastr.resources': resources_list,
                  'fastr.examples': examples_list,
                  'fastr.web': web_list,
                  'fastr': ['versioninfo']
                  },
    scripts=[],
    url='https://bitbucket.org/bigr_erasmusmc/fastr',
    license='Apache License 2.0',
    description='Workflow creation and batch execution environment.',
    long_description=_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Education',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Logging',
        'Topic :: Utilities',
    ],
    install_requires=_requires,
    tests_require=_tests_require,
    test_suite='nose.collector',
    cmdclass={'test': NoseTestCommand},
    entry_points=entry_points,
)
