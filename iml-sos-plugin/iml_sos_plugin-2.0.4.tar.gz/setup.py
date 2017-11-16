#!/usr/bin/env python

# Copyright (c) 2017 Intel Corporation. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.


from setuptools import setup, find_packages

setup(
    name='iml_sos_plugin',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    description='IML sosreport plugin',
    long_description="""
    A sosreport plugin for collecting IML data
    """,
    url='https://github.com/intel-hpdd/iml_sos_plugin',
    author='IML Team',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='IML lustre',
    packages=find_packages(exclude=['*tests*']),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'iml-diagnostics = iml_sos_plugin.cli:main',
            'chroma-diagnostics = iml_sos_plugin.cli:chroma_diagnostics'
        ]
    }
)
