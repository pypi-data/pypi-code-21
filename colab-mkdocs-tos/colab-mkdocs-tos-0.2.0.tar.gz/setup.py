#!/usr/bin/env python
"""
Colab Mkdocs Plugin
===================================
"""
from setuptools import setup, find_packages

install_requires = ['colab', 'mkdocs', 'mkdocs-material']

tests_require = ['mock']


setup(
    name="colab-mkdocs-tos",
    version='0.2.0',
    author='labhackercd',
    author_email='labhackercd@gmail.com',
    url='https://github.com/labhackercd/colab-mkdocs-plugin',
    description='Colab Mkdocs Plugin',
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
