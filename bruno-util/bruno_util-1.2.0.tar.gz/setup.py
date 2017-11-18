#!/usr/bin/env python

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='bruno_util',
      version='1.2.0',
      description='Catch-all package for utilities useful to Bruno Beltran',
      long_description=readme(),
      author='Bruno Beltran',
      author_email='brunobeltran0@gmail.com',
      packages=['bruno_util'],
      license='MIT',
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Topic :: Utilities'
      ],
      keywords='parameter scanning scientific search testing',
      url='https://github.com/brunobeltran/bruno_util',
      install_requires=['pscan'], # include other packages I wrote that are useful
     )
