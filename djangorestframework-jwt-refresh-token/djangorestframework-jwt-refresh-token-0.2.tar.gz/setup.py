#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ast
import codecs
import os

from setuptools import setup


class VersionFinder(ast.NodeVisitor):
    def __init__(self):
        self.version = None

    def visit_Assign(self, node):
        if node.targets[0].id == '__version__':
            self.version = node.value.s


def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(filename, encoding='utf-8') as fp:
        return fp.read()


def find_version(*parts):
    finder = VersionFinder()
    finder.visit(ast.parse(read(*parts)))
    return finder.version


name = 'djangorestframework-jwt-refresh-token'
package = 'refreshtoken'
version = find_version(package, '__init__.py')
description = 'Long Refresh Tokens for JSON Web Token based authentication'
url = 'https://github.com/lock8/django-rest-framework-jwt-refresh-token'
author = 'Nicolas Delaby'
author_email = 'nicolas@noa.one'
license = 'MIT'
install_requires = []


setup(
    name=name,
    version=version,
    url=url,
    license=license,
    description=description,
    long_description=read('README.md'),
    author=author,
    author_email=author_email,
    packages=[package],
    include_package_data=True,
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
