# -*- coding: utf-8 -*-

"""
Flask-pysnow
------------

Adds ServiceNow support to Flask applications with the help of the
`pysnow`_ library.

Links
`````

* `documentation <http://packages.python.org/Flask-pysnow`_

.. _pysnow: https://github.com/rbw0/pysnow

"""

import io
import ast

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version():
    """ Parses package __init__ file and fetches version attribute from the syntax tree
    :return: flask-pysnow version
    """
    with io.open('flask_pysnow/__init__.py') as input_file:
        for line in input_file:
            if line.startswith('__version__'):
                return ast.parse(line).body[0].value.s


with io.open('README.rst') as readme:
    setup(
        name='Flask-pysnow',
        version=get_version(),
        url='https://github.com/rbw0/flask-pysnow',
        license='MIT',
        author='Robert Wikman',
        author_email='rbw@vault13.org',
        maintainer='Robert Wikman',
        maintainer_email='rbw@vault13.org',
        description='Flask extension for pysnow',
        download_url='https://github.com/rbw0/flask-pysnow/tarball/%s' % get_version(),
        long_description=readme.read(),
        packages=['flask_pysnow'],
        zip_safe=False,
        include_package_data=True,
        platforms='any',
        install_requires=[
            'Flask',
            'oauthlib',
            'pysnow'
        ],
        classifiers=[
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
            'Topic :: Software Development :: Libraries :: Python Modules'
        ]
    )
