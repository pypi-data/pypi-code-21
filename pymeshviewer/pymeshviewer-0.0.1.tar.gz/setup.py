# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pymeshviewer',
    version='0.0.1',

    description='Parser for Meshviewer nodelists and topology files',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/blocktrron/pymeshviewer',

    # Author details
    author='blocktrron',
    author_email='david@darmstadt.freifunk.net',

    # Choose your license
    license='AGPLv3',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='development meshviewer freifunk',
    packages=['pymeshviewer', 'pymeshviewer.graph', 'pymeshviewer.nodelist', 'pymeshviewer.parser'],
    install_requires=[],
)