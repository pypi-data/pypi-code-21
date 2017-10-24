#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from distutils.core import Command


class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from django.conf import settings
        settings.configure(
            DATABASES={
                'default': {
                    'NAME': ':memory:',
                    'ENGINE': 'django.db.backends.sqlite3'
                }
            },
            INSTALLED_APPS=('calaccess_scraped',),
            MIDDLEWARE_CLASSES=()
        )
        from django.core.management import call_command
        import django
        django.setup()
        call_command('test', 'calaccess_scraped')


setup(
    name='django-calaccess-scraped-data',
    version='0.1.0rc1',
    license='MIT',
    description='A Django app to scrape campaign finance data from the '
                'California Secretary of State’s CAL-ACCESS database',
    author='California Civic Data Coalition',
    url='http://django-calaccess.californiacivicdata.org',
    author_email='cacivicdata@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,  # because we're including static files
    install_requires=(
        'django>=1.10',
        'beautifulsoup4>=4.6.0',
        'requests>=2',
    ),
    cmdclass={'test': TestCommand,},
    classifiers=(
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'License :: OSI Approved :: MIT License',
    ),
)
