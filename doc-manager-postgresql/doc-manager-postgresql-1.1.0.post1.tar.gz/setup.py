#!/usr/bin/env python
# coding: utf8

from setuptools import setup

setup(
        name='doc-manager-postgresql',
        version='1.1.0-1',
        description='Copy of Hopworks Doc Manager debugged when using several doc manager',
        platforms=["any"],
        author=u'Julie Rossi',
        author_email='julierossi06@gmail.com',
        install_requires=[
            'mongo_connector >= 2.5.1',
            'psycopg2 >= 2.6.1',
            'future >= 0.16.0',
            'jsonschema >= 2.6.0'
        ],
        tests_require=[
            'mock>=2.0.0',
            'aloe>=0.1.12',
            'testing.postgresql>=1.3.0',
            'mongo-orchestration>=0.6.9'
        ],
        license="http://www.apache.org/licenses/LICENSE-2.0.html",
        url='https://github.com/JulieRossi/mongo-connector-postgresql/tree/pypi',
        packages=["mongo_connector", "mongo_connector.doc_managers"],
        test_suite='tests'
)
