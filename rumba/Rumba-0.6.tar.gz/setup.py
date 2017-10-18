#!/usr/bin/env python

import setuptools


setuptools.setup(
    name='Rumba',
    version='0.6',
    url='https://gitlab.com/arcfire/rumba',
    keywords='rina measurement testbed',
    author='Sander Vrijders',
    author_email='sander.vrijders@ugent.be',
    license='LGPL',
    description='Rumba measurement framework for RINA',
    packages=['rumba', 'rumba.testbeds', 'rumba.prototypes'],
    install_requires=['paramiko', 'repoze.lru; python_version<"3.2"'],
    extras_require={'NumpyAcceleration': ['numpy']},
    scripts=['tools/rumba-access']
)
