"""Setup.py."""
from codecs import open
from os import path
from setuptools import setup, find_packages
from zenomatic import __version__


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

install_requires = [
    'colorama',
    'docopt'
]


setup(
    name='zenomatic',
    version=__version__,
    description='Get the Zen of Python in your Applications',
    long_description=long_description,
    author='Chris Maillefaud',
    author_email='chris@megalus.com.br',
    # Choose your license
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    keywords='geru dev challenge python zen',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'zenomatic=zenomatic.run:start'
        ],
    },
)
