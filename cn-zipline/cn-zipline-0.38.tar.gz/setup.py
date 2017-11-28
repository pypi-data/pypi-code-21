#!/usr/bin/env python

import distutils.sysconfig
from setuptools import setup, find_packages, Extension

try:
    import pypandoc

    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    long_description = ''

setup(
    name='cn-zipline',
    version='0.38',
    description='china zipline bundles',
    long_description=long_description,
    author='Jie Wang',
    author_email='790930856@qq.com',
    url='https://github.com/JaysonAlbert/cn_zipline',
    packages=find_packages(include=['cn_zipline', 'cn_zipline.*']),
    entry_points={
        'console_scripts': [
            'cn_zipline = cn_zipline.__main__:main',
        ],
    },

    data_files=[
        (distutils.sysconfig.get_python_lib() + "/cn_zipline/libs", ['cn_zipline/libs/tdx_api.pyd']),
    ],

    install_requires=[
        'tables',
        'numpy',
        'zipline-live',
        'pytdx',
        'cn-treasury_curve',
        'cn-stock-holidays',
        'tdx-wrapper'
    ]
)
