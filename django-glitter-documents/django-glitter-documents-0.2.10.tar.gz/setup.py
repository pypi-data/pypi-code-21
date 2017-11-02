#!/usr/bin/env python
from codecs import open

from setuptools import find_packages, setup

with open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()


setup(
    name='django-glitter-documents',
    version='0.2.10',
    description='Glitter Documents',
    long_description=readme,
    url='https://github.com/developersociety/django-glitter-documents',
    maintainer='Developer Society',
    maintainer_email='studio@dev.ngo',
    platforms=['any'],
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=[
        'django-glitter',
        'django-taggit>=0.21.3',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    license='BSD',
)
