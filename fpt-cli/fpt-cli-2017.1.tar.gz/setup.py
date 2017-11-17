# -*- coding: utf-8 -*-

import codecs
import os

from setuptools import find_packages, setup


# metadata
NAME = 'fpt-cli'
DESCRIPTION = ('Estadísticas de la primera división del fútbol argentino '
               'por línea de comandos.')
KEYWORDS = ['fútbol', 'argentina', 'resultados', 'estadísticas']
URL = 'https://github.com/el-ega/fpt-cli'
EMAIL = 'mbordese@gmail.com'
AUTHOR = 'Matias Bordese'
LICENSE = 'MIT'

# deps
REQUIRED = [
    'click>=5.0', 'demiurge>=0.2', 'requests>=2.7.0',
]

HERE = os.path.abspath(os.path.dirname(__file__))

# use README as the long-description
with codecs.open(os.path.join(HERE, 'README.rst'), "rb", "utf-8") as f:
    long_description = f.read()


# load __version__.py module as a dictionary
about = {}
with open(os.path.join(HERE, 'fpt/__version__.py')) as f:
    exec(f.read(), about)


setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    keywords=KEYWORDS,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages(exclude=('tests',)),
    entry_points={
        'console_scripts': ['fpt=fpt.main:main'],
    },
    install_requires=REQUIRED,
    include_package_data=True,
    license=LICENSE,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
    ],
    zip_safe=False,
)
