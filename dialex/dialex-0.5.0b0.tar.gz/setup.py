#!/usr/bin/env python

import io
import os
from setuptools import setup

path_readme = os.path.join(os.path.dirname(__file__), 'README.md')

try:
    import pypandoc
    README = pypandoc.convert(path_readme, 'rst')
except (IOError, ImportError):
    with io.open(path_readme, encoding='utf-8') as readme:
        README = readme.read()

setup(
    name='dialex',
    version='0.5.0b0',
    license='MIT License',
    packages=['dialex'],
    include_package_data=True,
    zip_safe=False,
    setup_requires=['pytest-runner', 'pypandoc'],
    tests_require=['pytest'],
    install_requires=['requests'],
    description='Python Client for HyperLab Dialex API',
    long_description=README,
    author='Riyadh Al Nur',
    author_email='riyadh.alnur@hyperlab.xyz',
    url='https://github.com/HyperLab-Solutions-Sdn-Bhd/dialex-sdk-python',
    keywords=['hyperlab', 'python', 'sdk', 'nlp'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
        'Development Status :: 4 - Beta',
    ]
)
