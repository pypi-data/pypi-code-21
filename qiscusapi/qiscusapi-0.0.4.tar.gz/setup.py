#!/usr/bin/env python3
"""Python wrapper for Qiscus SDK RESTful API"""
from setuptools import setup, find_packages

setup(
    name='qiscusapi',
    version='0.0.4',
    author='nurcholis art',
    author_email='nurcholisart@gmail.com',
    description='Python wrapper for Qiscus SDK RESTful API',
    license='MIT',
    url='https://bitbucket.org/nurcholisart/qiscus-sdk-python',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(),
    install_requires=['requests', 'json'],
)
