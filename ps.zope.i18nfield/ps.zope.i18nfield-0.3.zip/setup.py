# -*- coding: utf-8 -*-
"""Setup for ps.zope.i18nfield package."""

from setuptools import (
    find_packages,
    setup,
)
import sys

version = '0.3'
description = 'A zope.schema field for inline translations.'
long_description = ('\n'.join([
    open('README.rst').read(),
    'Contributors',
    '------------\n',
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read(),
]))

install_requires = [
    'setuptools',
    # -*- Extra requirements: -*-
    'ZODB3',
    'z3c.indexer',
    'zope.globalrequest',
    'zope.i18n',
    'zope.interface',
    'zope.schema',
]

test_requires = [
    'z3c.form [test]',
    'zope.browserpage',
    'zope.publisher',
    'zope.testing',
    'zope.traversing',
]

if sys.version_info[:3] < (2, 7, 0):
    test_requires.append('unittest2')


setup(
    name='ps.zope.i18nfield',
    version=version,
    description=description,
    long_description=long_description,
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Zope3",
        "Intended Audience :: Other Audience",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Zope",
    ],
    keywords='zope zope3 schema i18n z3c.form',
    author='Propertyshelf, Inc.',
    author_email='development@propertyshelf.com',
    url='https://github.com/propertyshelf/ps.zope.i18nfield',
    download_url='http://pypi.python.org/pypi/ps.zope.i18nfield',
    license='GPL',
    packages=find_packages('src', exclude=['ez_setup']),
    package_dir={'': 'src'},
    namespace_packages=['ps', 'ps.zope'],
    include_package_data=True,
    zip_safe=False,
    extras_require=dict(
        test=test_requires,
    ),
    install_requires=install_requires,
    entry_points="""
    # -*- Entry points: -*-
    """,
)
