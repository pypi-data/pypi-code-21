##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Setup
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    with open(os.path.join(os.path.dirname(__file__), *rnames)) as f:
        return f.read()

CHAMELEON_REQUIRES = [
    # Pins because of https://github.com/zopefoundation/z3c.template/pull/2
    'chameleon >= 3.0',
    'z3c.pt >= 3.1.0',
    'z3c.ptcompat >= 2.1.0',

]

TESTS_REQUIRE = CHAMELEON_REQUIRES + [
    'zope.testing',
    'zope.testrunner',
    'zope.traversing',
]

setup(
    name='z3c.template',
    version='3.0.0',
    author="Roger Ineichen and the Zope Community",
    author_email="zope-dev@zope.org",
    description="A package implementing advanced Page Template patterns.",
    long_description=(
        read('README.rst')
        + '\n\n.. contents::\n\n'+
        read('src', 'z3c', 'template', 'README.rst')
        + '\n' +
        read('src', 'z3c', 'template', 'zcml.rst')
        + '\n' +
        read('CHANGES.rst')
        ),
    license="ZPL 2.1",
    keywords="zope3 template layout zpt pagetemplate",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'
    ],
    url='https://github.com/zopefoundation/z3c.template',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['z3c'],
    extras_require={
        'test': TESTS_REQUIRE,
        'chameleon': CHAMELEON_REQUIRES,
    },
    install_requires=[
        'setuptools',
        'zope.browserpage',
        'zope.component',
        'zope.configuration',
        'zope.interface',
        'zope.pagetemplate',
        'zope.publisher',
        'zope.schema',
    ],
    tests_require=TESTS_REQUIRE,
    test_suite='z3c.template.tests.test_suite',
    include_package_data=True,
    zip_safe=False,
)
