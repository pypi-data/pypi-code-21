# -*- coding: UTF-8 -*-

from distutils.core import setup
from setuptools import find_packages

setup(
    name='carrack',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    version='0.0.1dev1',
    description='Airflow Carrack Sync Replicator Marketplace Client',
    author='Raymond Joseph Usher Roche',
    author_email='rjsuher+pypi@gmail.com',
    install_requires=['airflow', 'click'],
    url='https://gitlab.com/fluyt/carrack',
    download_url='https://gitlab.com/fluyt/carrack/repository/v0.0.1dev1/archive.tar.gz',
    license='MIT',
    keywords=['airflow', 'sync', 'replication'],
    classifiers=[
        'Framework :: IPython',
        'Environment :: Console',
        'Topic :: Internet',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Terminals',
    ]
)
