'''
Created on Oct 10, 2017

@author: Roni Eliezer
'''

from setuptools import setup

setup(
    name="pytest-ochrus",
    packages = ['pytest_ochrus'],

    version = "0.0.2",
    license = "MIT",
    #use_scm_version=True,
    #setup_requires=['setuptools_scm'],
    #zip_safe=False,
    description='pytest results data-base and HTML reporter',
    long_description=open('README.rst').read(),
    url='https://github.com/ochrus/pytest-ochrus',
    author='Roni Eliezer',
    author_email='roniezr@gmail.com',

    # the following makes a plugin available to pytest
    entry_points = {
        'pytest11': [
            'pytest-ochrus = pytest_ochrus.plugin',
        ]
    },

    # custom PyPI classifier for pytest plugins
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Developers',
        "Framework :: Pytest",
    ],
    
    keywords=['pytest results data-base and HTML reporter'],
    install_requires=['pytest', 'requests'],
)
