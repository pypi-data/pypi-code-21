from os import path

from setuptools import setup

here = path.abspath(path.dirname(__file__))

setup(
    name='pymeshviewer',
    version='0.1.0',

    description='Parser for Meshviewer nodelists and topology files',

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
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='development meshviewer freifunk',
    packages=['pymeshviewer'],
    install_requires=[],
)
