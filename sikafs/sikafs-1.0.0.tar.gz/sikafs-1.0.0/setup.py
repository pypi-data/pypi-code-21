#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='sikafs',
    version='1.0.0',
    url = 'https://github.com/ondrejsika/sikafs',
    license = 'MIT',
    description = 'Sika File Server',
    author = 'Ondrej Sika',
    author_email = 'ondrej@ondrejsika.com',
    scripts = [
        'sikafsd',
        'sikafs',
    ],
    install_requires = [
        'flask',
        'requests',
    ],
)
