#!/usr/bin/env python

from setuptools import setup, find_packages

setup_requires = []

install_requires = ['pyyaml']

dev_requires = [
    'mock==2.0.0',
]


setup(
    name='dbtrolls',
    version='1.0',
    author='Marcos Caputo',
    author_email='caputo.marcos@gmail.com',
    url='https://github.com/caputomarcos/dbtrolls',
    description="dbtrolls - A simple tool to make Dev's life happy.",
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['docs', ]),
    zip_safe=True,
    install_requires=install_requires,
    extras_require={
        'dev': install_requires + dev_requires,
    },
    license='GPL',
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'dbtrolls = dbtrolls.__main__:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 3',
    ],
)
