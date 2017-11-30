#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name = "gn_gsimporter",
    version = "1.0.1",
    description = "GeoNode GeoServer Importer Client",
    keywords = "GeoNode GeoServer Importer",
    license = "MIT",
    url = "https://github.com/GeoNode/gsimporter",
    author = "Ian Schneider",
    author_email = "ischneider@opengeo.org",
    install_requires = [
        'httplib2',
    ],
    tests_require = [
        'gisdata>=0.5.4',
        'gsconfig>=1.0.0',
        'psycopg2',
        'OWSLib>=0.7.2',
        'unittest2',
    ],
    package_dir = {'':'src'},
    packages = find_packages('src'),
    test_suite = 'test.uploadtests'
)
