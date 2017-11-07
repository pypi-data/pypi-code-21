#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import io
from shutil import rmtree

from setuptools import find_packages, setup, Command

import keyring
import keyring.util.platform_


# Needed for the following functions
here = os.path.abspath(os.path.dirname(__file__))


# Load the package's __version__.py module as a dictionary.
about = {}
with io.open(os.path.join(here, 'hoops', '__version__.py')) as f:
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

    # Name of the package
    name=about['name'],

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=about['version'],

    description=about['description'],
    long_description=get_long_description(),

    # The project's main homepage.
    url=about['url'],

    # Author details
    author=about['author'],
    author_email=about['author_email'],

    # Choose your license
    # Don't forget to the license file
    license=about['license'],

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],

    # What does your project relate to?
    keywords='packaging setuptools development',

    # Adding Non-Code Files :
    # In order for these files to be copied at install time to the package’s folder inside site-packages,
    # you’ll need to supply :
    include_package_data=True,

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['twine', 'keyring', 'requests'],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    # See https://setuptools.readthedocs.io/en/latest/setuptools.html#automatic-script-creation
    entry_points=dict(console_scripts=['hoops-factory=hoops:cli']),

    cmdclass={
        'upload': SecureUploadCommand,
    },
)
