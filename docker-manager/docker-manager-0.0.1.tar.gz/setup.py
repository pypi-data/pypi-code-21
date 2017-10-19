#!/usr/bin/env python3

from setuptools import setup

setup(
    name='docker-manager',
    version='0.0.1',
    description='Tool for container management',
    author='Claudio Walser',
    author_email='claudio.walser@srf.ch',
    url='https://github.com/claudio-walser/python-docker-manager',
    packages=[
        '.',
        'dockerManager',
        'dockerManager.bin',
        'dockerManager.plugins'
    ],
    install_requires=['simple-cli', 'pyyaml', 'argparse', 'argcomplete', 'shutilwhich'],
    entry_points={
        'console_scripts': [
            'docker-image = dockerManager.bin.image:main',
            'docker-container = dockerManager.bin.container:main',
            'docker-watcher = dockerManager.bin.watcher:main',
            'docker-bridge = dockerManager.bin.bridge:main'
        ]
    }
)
