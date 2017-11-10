# -*- coding: utf-8 -*-

import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

import keyring
import keyring.util.platform_


# Needed for the following functions
here = os.path.abspath(os.path.dirname(__file__))


# Load the package's __version__.py module as a dictionary.
def get_version(package):
    about = {}
    with open(os.path.join(here, package, '__version__.py')) as f:
        exec(f.read(), about)

    return about['version']


# Get the long description from the README file
def get_long_description():

    with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()

    return long_description


class SecureUploadCommand(Command):
    """
    python setup.py upload --repository pypi
    python setup.py upload --repository testpypi
    """

    description = 'Build and publish the package.'
    user_options = [('repository=', 'r', 'repository')]
    servers = ['pypi', 'testpypi']

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        self.repository = None

    def finalize_options(self):
        if self.repository and self.repository in self.servers:
            self.server = self.repository
        else:
            raise Exception("Missing repository argument [ 'pypi' or 'testpypi' ]")

    def get_credentials(self):

        self.status('Getting credentials')

        # Getting the keyring data from the filesystem
        keyring.get_keyring()

        # Then get the password
        self.username = "Germione"
        self.password = keyring.get_password("pypi", self.username)

    def build_sdist(self):

        self.status('Building Source distribution...')
        os.system('{0} setup.py sdist'.format(sys.executable))

    def build_wheel(self):

        self.status('Building Wheel (universal) distribution...')
        os.system('{0} setup.py sdist bdist_wheel'.format(sys.executable))

    def twine(self):
        self.status('Uploading the package to PyPi via Twine…')
        os.system('twine upload -r {0} -u {1} -p {2} dist/*'.format(self.server, self.username, self.password))

    def run(self):
        try:
            self.status('Removing previous builds...')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.get_credentials()

        self.build_sdist()

        self.build_wheel()

        self.twine()

        sys.exit()


setup(
    name='manga_notifier',

    version=get_version('manga_notifier'),

    description='A command-line tool to keep updated of the new chapters manga.',

    long_description=get_long_description(),

    url='https://github.com/Germione/manga-notifier',

    author='Jerome Pradier',
    author_email='jerome.pradier@gmail.com',

    license='MIT',

    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],

    keywords='tools manga entertainement',

    include_package_data=True,

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    install_requires=['twine', 'keyring', 'requests', 'beautifulsoup4', 'lxml', 'click'],

    entry_points=dict(console_scripts=['manga-notifier=manga_notifier:cli']),

    # $ setup.py publish support.
    cmdclass={
        'upload': SecureUploadCommand,
    },
)
