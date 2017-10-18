# -*- coding: utf-8 -*-
"""
python-socketio-client
----------------------

Socket.IO client.
"""
from setuptools import setup

setup(
    name='python-socketio-client',
    version='1.1',
    url='http://github.com/utkarsh-vishnoi/python-socketio-client/',
    license='MIT',
    author='Utkarsh Vishnoi',
    author_email='utkarshvishnoi25@gmail.com',
    description='Socket.IO client',
    long_description=open('README.rst').read(),
    packages=['socketio_client'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'python-engineio-client>=1.1',
        'gevent>=1.0.2',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

