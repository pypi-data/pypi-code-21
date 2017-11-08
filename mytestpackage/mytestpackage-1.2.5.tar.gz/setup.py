"""
A setup.py file based on the kennethreitz/setup.py on GitHub.
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install twine

import os
import sys
from shutil import rmtree
from setuptools import find_packages, setup, Command

# Package meta-data.
NAME = 'mytestpackage'
DESCRIPTION = 'A short description of the python package.'
LONGDESCRIPTION = 'See the README.md file on GitHub for more information.'
URL = 'https://github.com/user/mytestpackage'
EMAIL = 'me@example.com'
AUTHOR = 'Homer Simpson'
VERSION = '1.2.5'

# What packages are required for this module to be executed?
REQUIRED = [
    # 'requests', 'maya', 'records',
]


# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        """Initialization options."""
        pass

    def finalize_options(self):
        """Finalize options."""
        pass

    def run(self):
        """Remove previous builds."""
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPi via Twine…')
        os.system('twine upload dist/*')

        sys.exit()


# Where the magic happens:
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONGDESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages(exclude=('tests',)),
    install_requires=REQUIRED,
    include_package_data=True,
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list at https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
    },
)

