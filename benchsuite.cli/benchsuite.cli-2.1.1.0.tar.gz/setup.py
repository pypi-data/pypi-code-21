# Benchmarking Suite
# Copyright 2014-2017 Engineering Ingegneria Informatica S.p.A.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Developed in the ARTIST EU project (www.artist-project.eu) and in the
# CloudPerfect EU project (https://cloudperfect.eu/)

import os
from setuptools import setup, find_packages
from setuptools.command.install import install

# import the VERSION from the source code
import sys
sys.path.append(os.getcwd() + '/src/benchsuite')
from cli import VERSION


class CustomInstallCmd(install):
    """
    Custom install command that before running the actual install command.
    Invoke the argparse-manpage to build the manpage from the argparse parser of the cli.
    """
    def run(self):

        # import here build_manpage because argparse-manpage could be not available the first time setup.py is invoked
        from build_manpage import build_manpage

        # define it as command
        self.distribution.cmdclass['build_manpage'] = build_manpage

        # run the command
        sys.path.insert(0, 'src/')  # add src dir to the path so build_manpage can find the cli module
        self.run_command('build_manpage')

        # run the standard install command
        # do not call do_egg_install() here because it would do an egg and not install the manpage
        # TODO: create a script to install the manpage from the egg resource (if we want to use the
        # standard do_egg_install() command
        install.run(self)



setup(
    name='benchsuite.cli',
    version='.'.join(map(str, VERSION)),

    description='A command line interface for the Benchmarking Suite',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),

    url='https://github.com/benchmarking-suite/benchsuite-cli',

    author='Gabriele Giammatteo',
    author_email='gabriele.giammatteo@eng.it',

    license='Apache',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Topic :: System :: Benchmark',
        'Topic :: Utilities',
        'Topic :: Software Development :: Testing',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3 :: Only',
        'Environment :: Console',
        'Operating System :: Unix'
    ],
    keywords='benchmarking cloud testing performance',


    packages=find_packages('src'),
    namespace_packages=['benchsuite'],
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': ['benchsuite=benchsuite.cli.command:main'],
    },
    data_files = [('man/man1', ['benchsuite.1'])],

    setup_requires=['argparse-manpage==0.0.1'],
    install_requires=['prettytable', 'benchsuite.core'],
    dependency_links=[
        'https://github.com/gabrielegiammatteo/build_manpage/zipball/master#egg=argparse-manpage-0.0.1'
    ],

    cmdclass={'install': CustomInstallCmd},
)