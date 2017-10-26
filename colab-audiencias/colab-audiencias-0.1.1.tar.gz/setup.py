#!/usr/bin/env python
"""
Colab Audiencias Plugin
===================================
"""
from setuptools import setup, find_packages

install_requires = ['colab']

tests_require = ['mock']


setup(
    name="colab-audiencias",
    version='0.1.1',
    author='labhackercd',
    author_email='labhackercd@gmail.com',
    url='https://github.com/labhackercd/colab-audiencias-plugin',
    description='Colab Audiencias Plugin',
    long_description=__doc__,
    license='GPLv3',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    zip_safe=False,
    install_requires=install_requires,
    test_suite="tests.runtests.run",
    tests_require=tests_require,
    extras_require={'test': tests_require},
    include_package_data=True,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
