"""
Setup for buche
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='buche',
    version='0.1.4',

    description='Pretty-print Python objects to Buche logger.',
    long_description=long_description,

    url='https://github.com/breuleux/buche',

    author='Olivier Breuleux',
    author_email='breuleux@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='buche repr pprint html development',

    packages=find_packages(exclude=['contrib', 'doc', 'tests']),

    install_requires=['hrepr'],

    extras_require={
        'dev': [],
        'test': [],
    },

    # package_data={
    #     'buche': ['style/*.css'],
    # },

    python_requires='>=3.6',
)
