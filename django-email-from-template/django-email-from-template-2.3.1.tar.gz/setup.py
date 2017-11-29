#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='django-email-from-template',
    description="Send emails generated entirely from Django templates.",
    version='2.3.1',
    url='https://chris-lamb.co.uk/projects/django-email-from-template',

    author="Chris Lamb",
    author_email='chris@chris-lamb.co.uk',
    license="BSD",

    packages=find_packages(),
    package_data={'': [
        'templates/*/*',
    ]},

    install_requires=(
        'Django>=1.8',
    ),
)
