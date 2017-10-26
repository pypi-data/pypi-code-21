# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='getignore',

    version='0.1.3',

    description='Command line utility to download common .gitignore files',
    long_description=long_description,

    url='https://github.com/Jackevansevo/getignore',

    author='Jack Evans',
    author_email='jack@evans.gb.net',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python :: 3',
    ],

    keywords='sample setuptools development',

    py_modules=['getignore'],

    install_requires=['prompt_toolkit'],

    entry_points={
        'console_scripts': [
            'getignore=getignore:main'
        ]
    },
)
