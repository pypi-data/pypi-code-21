# -*- coding: utf-8 -*-

import os
import sys
import io
from shutil import rmtree

from setuptools import find_packages, setup, Command

import keyring


# Needed for the following functions
here = os.path.abspath(os.path.dirname(__file__))


# Load the package's __version__.py module as a dictionary.
about = {}
with io.open(os.path.join(here, 'manga_notifier', '__version__.py')) as f:
    exec(f.read(), about)


# Get the long description from the README file
def get_long_description():

    with io.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
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
            raise Exception("Missing repository argument ['pypi'/'testpypi']")

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
    name=about['name'],

    version=about['version'],

    description=about['description'],

    long_description=get_long_description(),

    url=about['url'],

    author=about['author'],
    author_email=about['author_email'],

    license=about['license'],

    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers

        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='tools manga entertainement',

    include_package_data=True,

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    install_requires=['requests', 'lxml', 'cssselect', 'click'],

    entry_points=dict(console_scripts=['manga-notifier=manga_notifier:cli']),

    # $ setup.py publish support.
    cmdclass={
        'upload': SecureUploadCommand,
    },
)
