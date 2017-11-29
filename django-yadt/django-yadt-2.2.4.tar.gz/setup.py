#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='django-yadt',

    url='https://chris-lamb.co.uk/projects/django-yadt',
    version='2.2.4',
    description="Yet Another Django Thumbnailer",

    author="Chris Lamb",
    author_email='chris@chris-lamb.co.uk',
    license='BSD',

    packages=find_packages(),

    install_requires=(
        'Django>=1.8',
        'Pillow',
    ),
)
