# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

version = '5.0.1'

setup(
    name='Products.statusmessages',
    version=version,
    description='statusmessages provides an easy way of handling '
                'internationalized status messages managed via an '
                'BrowserRequest adapter storing status messages in '
                'client-side cookies.',
    long_description=(open('README.rst').read() + '\n' +
                      open('CHANGES.rst').read()),
    classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 5.0',
        'Framework :: Plone :: 5.1',
        'Framework :: Zope2',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='Zope CMF Plone status messages i18n',
    author='Hanno Schlichting',
    author_email='plone-developers@lists.sourceforge.net',
    url='https://pypi.python.org/pypi/Products.statusmessages',
    license='BSD',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['Products'],
    include_package_data=True,
    zip_safe=False,
    extras_require=dict(
        test=[
            'zope.component',
            'Zope2',
        ],
    ),
    install_requires=[
        'setuptools',
        'zope.annotation',
        'zope.i18n',
        'zope.interface',
    ],
)
