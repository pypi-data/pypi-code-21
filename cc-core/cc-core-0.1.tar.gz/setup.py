#!/usr/bin/env python3

from distutils.core import setup

setup(
    name='cc-core',
    version='0.1',
    summary='Curious Containers is an application management service that is able to execute thousands of '
            'short-lived applications in a distributed cluster by employing Docker container engines.',
    description='Curious Containers is an application management service that is able to execute thousands of '
                'short-lived applications in a distributed cluster by employing Docker container engines.',
    author='Christoph Jansen, Michael Witt, Maximilian Beier',
    author_email='Christoph.Jansen@htw-berlin.de',
    url='https://github.com/curious-containers/cc-agent',
    packages=[
        'cc_core',
        'cc_core.commons',
        'cc_core.commons.schemas',
        'cc_core.agent'
    ],
    license='Apache-2.0',
    platforms=['any'],
    install_requires=[
        'flask',
        'requests',
        'jsonschema',
        'ruamel.yaml'
    ]
)
