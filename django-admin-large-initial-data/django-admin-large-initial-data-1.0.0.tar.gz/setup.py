#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

package_name = 'large_initial'


def runtests():
    import os
    import sys

    import django
    from django.core.management import call_command

    os.environ['DJANGO_SETTINGS_MODULE'] = 'test_project.settings'
    django.setup()
    call_command('test', 'test_project.main.tests')
    sys.exit()


setup(
    name='django-admin-large-initial-data',
    version='1.0.0',
    description="Allow to make redirects with large session "
    "data to django ModelAdmin add view",
    author='Petr Dlouhý',
    author_email='petr.dlouhy@email.cz',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='django admin initial_data',
    url='https://github.com/PetrDlouhy/django-admin-large-initial-data',
    download_url='https://github.com/PetrDlouhy/'
    'django-admin-large-initial-data',
    license='GPL',
    install_requires=[
        'django>=1.9',
        'six',
    ],
    packages=[
        package_name,
    ],
    include_package_data=True,
    zip_safe=False,
    test_suite='setup.runtests',
)
