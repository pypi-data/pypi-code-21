from setuptools import setup, find_packages
from os.path import join
import sys
import os

NAME = 'Products.ZSPARQLMethod'
PATH = NAME.split('.') + ['version.txt']
VERSION = open(join(*PATH)).read().strip()

install_requires = ['sparql-client', 'eventlet']
if sys.version_info < (2, 6):
    install_requires += ['simplejson']

docs = open('README.rst').read() + "\n" + \
       open(os.path.join("docs", "HISTORY.txt")).read()

setup(
    name=NAME,
    version=VERSION,
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Framework :: Zope2",
        "Framework :: Plone",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Zope",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License (GPL)",
    ],
    keywords='EEA Add-ons Plone Zope',
    author='European Environment Agency: IDM2 A-Team',
    author_email="eea-edw-a-team-alerts@googlegroups.com",
    url='https://github.com/eea/Products.ZSPARQLMethod',
    license='GPL',
    description="Zope product for making SPARQL queries, simiar to ZSQLMethod",
    long_description=docs,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
        'test': [
            'mock',
            'mechanize==0.2.5',
            'wsgi_intercept==0.4',
            'webob',
        ]
    },
)
