"""Tabs - Import tables in a consistent, maintainable, and readable way.

Tabs is a Micro framework for defining and loading tables in a consistent way.
The goal is to make data science projects more maintainable by
improving code readability.

Tabs comes with support for caching processed tables based on the current
configuration resulting in shorter loading of tables that have already been
compiled once.

Link to full documentation: http://tabs.readthedocs.io/en/latest/index.html
"""
from setuptools import setup

setup(name='tabs',
      version='0.7.0',
      url='https://github.com/ohenrik/tabs',
      description="""Tabs - Import tables in a consistent, maintainable, and readable way""",
      long_description=__doc__,
      author='Ole Henrik Skogstrøm',
      author_email='ole@amplify.no',
      packages=['tabs'],
      install_requires=[
          'pandas>=0.20',
          'dill>=0.2'
      ],
      classifiers=[
          'Development Status :: 2 - Pre-Alpha'
      ]
     )

__author__ = 'Ole Henrik Skogstrøm'
