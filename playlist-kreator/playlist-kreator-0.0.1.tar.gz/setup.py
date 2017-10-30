# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

from playlist_kreator import VERSION

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read().split('\n')

setup(
    name='playlist-kreator',
    version=VERSION,
    description='Create playlists easily from a list of artists, using their top songs.',
    long_description=long_description,
    url='https://github.com/epayet/playlist_kreator',
    author='Emmanuel Payet',
    author_email='contact@emmanuel-payet.me',
    license='MIT',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Internet',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='music googlemusic playlist',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=requirements,
    scripts=['bin/playlist-kreator'],
)
