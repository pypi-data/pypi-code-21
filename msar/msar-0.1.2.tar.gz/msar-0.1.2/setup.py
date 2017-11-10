# -*- encoding: UTF-8 -*-
from setuptools import setup, find_packages
from codecs import open
from os import path

VERSION = '0.1.2'
here = path.abspath(path.dirname(__file__))
# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_des = f.read()

setup(
    name='msar',
    version=VERSION,
    python_requires='>=2.7',
    description="My System Activity Reporter",
    long_description=long_des,
    author='Askdaddy',
    author_email='askdaddy@gmail.com',
    url='https://github.com/askdaddy/msar',
    entry_point={'console_scripts': ['msar=msar.command_line:main']},
    keywords=['linux', 'system', 'monitor']
)
