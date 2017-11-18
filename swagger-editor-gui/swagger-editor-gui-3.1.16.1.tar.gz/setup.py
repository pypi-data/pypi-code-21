#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='swagger-editor-gui',
    version='3.1.16.1',
    packages=find_packages(),
    include_package_data=True,
    author='Victor Häggqvist',
    author_email='pypi@snilius.com',
    url='https://victorhaggqvist.com',
    entry_points = {
        'gui_scripts': [
            'swagger-editor-gui = gui.gui:main'
        ]
    }
)
