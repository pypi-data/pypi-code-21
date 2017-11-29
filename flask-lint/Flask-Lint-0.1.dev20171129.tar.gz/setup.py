# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

setup(
    name='Flask-Lint',
    version='0.1',
    url='https://github.com/tangwz/flask-lint',
    license='BSD',
    author='Tangwz',
    author_email='tangwz.com@gmail.com',
    description='Simple integration of Flask and jsonlint.',
    packages=find_packages(exclude=('tests',)),
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
        'jsonlint',
        'itsdangerous',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
