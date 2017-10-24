#!/usr/bin/env python

from distutils.core import setup

from setuptools import find_packages

setup(
    name='django-automationcommon',
    # When changing this version number, remember to update CHANGELOG.
    version='1.12',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='Common functionality across different Django projects of the UofC UIS Automation team',
    long_description=open('README.rst').read(),
    url='https://git.csx.cam.ac.uk/i/ucs/automation/django-automationcommon',
    author='Automation team, University Information Services, University of Cambridge',
    author_email='automation@uis.cam.ac.uk',
    tests_require=['testfixtures'],
    install_requires=[
        'django>=1.8,<1.12',
        'django-ucamlookup>=1.9.2',
        'requests',
        'celery<4',
        'python-dateutil',
        'zeep',
        'django-hijack',
        'django-stronghold',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
