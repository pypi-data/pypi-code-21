# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""

from setuptools import setup
from pip.req import parse_requirements

setup(
    name='qdrouter-jinja2',
    version='0.1.8',
    packages=['qdrouterJinja2'],
    entry_points={
        "console_scripts": ['qdrouterJinja2 = qdrouterJinja2.qdrouterJinja2:main']
    },
    license='Apache 2.0',
    description='Generate qpid-dispatch config (qdrouter.conf) as Jinja2 template from already'
                ' installed qpid-dispatch.',
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    install_requires=[
        'argparse'
    ],
    url='https://github.com/rh-messaging-qe/qdrouterd-jinja2',
    author='Dominik Lenoch <dlenoch@redhat.com>, Jakub Stejskal <jstejska@redhat.com>',
    author_email='dlenoch@redhat.com'
)
