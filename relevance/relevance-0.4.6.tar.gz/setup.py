#!/usr/bin/python3

# pylint: disable-all

import distutils
from setuptools import setup
from setuptools import find_packages

import relevance as main


class CleanCommand(distutils.cmd.Command):  # type: ignore
    description = 'clean the directory from build files'
    user_options = []  # type: ignore

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import os
        from shutil import rmtree
        dirs = [
            '.mypy_cache/',
            'docs/apidoc',
            'build/', 'dist/', '{0}.egg-info/'.format(main.__name__), '.eggs',
        ]
        for dir in dirs:
            rmtree(dir, ignore_errors=True)
        for root, subdirs, files in os.walk('.'):
            rmtree('{0}/__pycache__/'.format(root), ignore_errors=True)


class BuildApidocCommand(distutils.cmd.Command):  # type: ignore
    description = 'build the api documentation'
    user_options = []  # type: ignore

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys
        from sphinx.apidoc import main as apidoc
        if apidoc(['setup.py', '-f', '-e', '-o', 'docs/apidoc', main.__name__]) > 0:
            sys.exit(1)


class BuildSphinxCommand(distutils.cmd.Command):  # type: ignore
    description = 'build the Sphinx documentation'
    user_options = []  # type: ignore

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys
        from sphinx import main as sphinx
        if sphinx(['setup.py', 'docs/', 'build/docs/']) > 0:
            sys.exit(1)


class ValidateCommand(distutils.cmd.Command):  # type: ignore
    description = 'check source files for errors and warnings'
    user_options = []  # type: ignore

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import os, sys

        if os.fork() == 0:
            from mypy.main import main as mypy
            mypy('', args=[main.__name__])
            return
        _, ex_mypy = os.wait()

        if os.fork() == 0:
            from pylint.lint import Run as pylint
            pylint([main.__name__])
            return
        _, ex_lint = os.wait()

        if ex_lint + ex_mypy > 0:
            sys.exit(1)


setup(
    name=main.__name__,
    version=main.__version__,

    description=main.__doc__.split('\n')[1].strip(),
    long_description=main.__doc__.strip(),
    url='http://www.relevance.io',
    author='OverrideLogic',
    author_email='info@overridelogic.com',
    maintainer=main.__author__,
    maintainer_email=main.__author_email__,

    license=main.__license__,
    platforms=['any'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search'
    ],

    packages=find_packages(exclude=['tests', 'tests.*']),
    provides=[main.__name__],

    cmdclass={
        'clean': CleanCommand,
        'build_apidoc': BuildApidocCommand,
        'build_sphinx': BuildSphinxCommand,
        'validate': ValidateCommand,
    },

    python_requires='>=3.5',
    setup_requires=[
        'Sphinx>=1.6.5',
        'pylint>=1.7.4',
        'mypy>=0.550',
    ],
    tests_require=[],
    test_suite='tests',

    install_requires=[
        'Werkzeug>=0.12.2',
        'Flask>=0.12',
        'anyconfig>=0.9.1',
        'PyYAML>=3.12',
        'Twisted>=17.9.0',
        'python-dateutil>=2.6.1',
        'requests>=2.9.1',
    ],

    entry_points={
        'console_scripts': [
            'relevance=relevance.utils.cli:main',
            'relevance-server=relevance.utils.cli:server',
            'relevance-search=relevance.utils.cli:search',
        ],
    },

    data_files=[
        ('/etc/relevance', [
            'etc/search.json-example',
        ]),
    ],
)
