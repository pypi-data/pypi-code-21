""" Installer
"""
import os
from setuptools import setup, find_packages

NAME = 'eea.relations'
PATH = NAME.split('.') + ['version.txt']
VERSION = open(os.path.join(*PATH)).read().strip()

setup(name=NAME,
      version=VERSION,
      description=("EEA Possible Relations. This package provides a flexible "
                   "way to manage relations in a Plone site. it provides a new "
                   "reference browser widget and a central management "
                   "interface for relations, their labels and requirements."),
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Framework :: Zope2",
          "Framework :: Plone",
          "Framework :: Plone :: 4.0",
          "Framework :: Plone :: 4.1",
          "Framework :: Plone :: 4.2",
          "Framework :: Plone :: 4.3",
          "Programming Language :: Zope",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "License :: OSI Approved :: GNU General Public License (GPL)",
      ],
      keywords='EEA Add-ons Plone Zope',
      author='European Environment Agency: IDM2 A-Team',
      author_email='eea-edw-a-team-alerts@googlegroups.com',
      url='https://github.com/collective/eea.relations',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['eea',],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'pydot',
          'eea.jquery > 8.0',
          'eea.facetednavigation',
          'plone.api',
          'plone.stringinterp >= 1.0.14',
          'Products.TALESField',
      ],
      extras_require={
          'test': [
              'plone.app.testing',
          ],
          'yum': [
              'graphviz',
              'graphviz-devel',
              ],
          'apt': [
              'graphviz',
              'libgraphviz-dev',
          ],
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """
      )
