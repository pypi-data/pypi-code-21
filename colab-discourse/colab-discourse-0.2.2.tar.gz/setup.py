#!/usr/bin/env python
"""
Colab Discourse Plugin
===================================
"""
from setuptools import setup, find_packages

install_requires = ['colab', 'pydiscourse']

tests_require = ['mock']


setup(
    name="colab-discourse",
    version='0.2.2',
    author='labhackercd',
    author_email='labhackercd@gmail.com',
    url='https://github.com/labhackercd/colab-discourse-plugin',
    description='Colab Discourse Plugin',
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
