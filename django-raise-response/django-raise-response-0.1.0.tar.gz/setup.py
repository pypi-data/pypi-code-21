#!/usr/bin/env python
import io
import os
import sys

from setuptools import find_packages, setup


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()


readme = io.open('README.rst', 'r', encoding='utf-8').read()

setup(
    name='django-raise-response',
    description='Raise any response object in Django',
    long_description=readme,
    url='https://github.com/wearewhys/django-raise-response',
    author='Jacopo Cascioli',
    author_email='jacopocascioli@gmail.com',
    license='MIT',
    version='0.1.0',
    packages=find_packages(),
    tests_require=[],
    setup_requires=[],
    install_requires=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Framework :: Django'
    ]
)
