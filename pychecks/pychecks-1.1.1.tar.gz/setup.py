#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='pychecks',
    version='1.1.1',
    description=(
        'check tools'
    ),
    long_description='check tools',
    author='chendansi',
    author_email='289908221@qq.com',
    maintainer='chendansi',
    maintainer_email='289908221@qq.com',
    license='MIT',
    packages=find_packages(),
    platforms=["all"],
    install_requires=[
        'pylint'
    ],
    url='https://www.baidu.com',
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Utilities",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ],
    entry_points={
        "console_scripts": [
            "pychecks = pychecks.__main__:main",
        ],
    },
)
