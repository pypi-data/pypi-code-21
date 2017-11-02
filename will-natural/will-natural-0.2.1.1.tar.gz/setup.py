#!/usr/bin/env python

try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(name='will-natural',
    version='0.2.1.1',
    description='Convert data to their natural (human-readable) format',
    long_description='''
This is a *temporary* fork of the `official natural <https://github.com/tehmaze/natural>` repo to add Python 3 support, and allow pip to keep working with the behavior changes with the --process-dependency-links deprecation.

Once `the python 3 pull request <https://github.com/tehmaze/natural/pull/13>` is merged and a new version is released, this package will be deleted.

Example Usage
=============

Basic usage::

    >>> from natural.file import accessed
    >>> print accessed(__file__)
    just now

We speak your language (with `your support`_)::

    >>> import locale
    >>> locale.setlocale(locale.LC_MESSAGES, 'nl_NL')
    >>> print accessed(__file__)
    zojuist

Bugs/Features
=============

You can issue a ticket in GitHub: https://github.com/tehmaze/natural/issues

Documentation
=============

The project documentation can be found at http://natural.rtfd.org/

.. _your support: http://natural.readthedocs.org/en/latest/locales.html
''',
    author='Steven Skoczen (fork only).  Original author is Wijnand Modderman-Lenstra',
    author_email='steven@heywill.io',
    license='MIT',
    keywords='natural data date file number size',
    url='https://github.com/tehmaze/natural',
    packages=['natural'],
    package_data={'natural': ['locales/*/LC_MESSAGES/*.mo']},
    install_requires=['six'],
)
