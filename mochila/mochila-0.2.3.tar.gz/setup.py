import io
import os

from setuptools import setup

import mochila

here = os.path.abspath(os.path.dirname(__file__))


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.rst', 'CHANGELOG.rst')

setup(
    name='mochila',
    version=mochila.__version__,
    packages=['mochila'],
    include_package_data=True,
    package_data={'mochila': ['CONTRIB.rst', 'CHANGELOG.rst']},
    # Metadata
    author='Horacio Hoyos Rodriguez',
    author_email='arcanefoam@gmail.com',
    description='Provides collections and a powerful API to process data in those collections in a declarative way.',
    url='http://bitbucket.org/arcanefoam/mochila',
    long_description=long_description,
    platforms='any',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 5 - Production/Stable',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
