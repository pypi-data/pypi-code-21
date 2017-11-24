from setuptools import setup, find_packages
import os

version = '1.1.1'

setup(name='cs.commenteditor',
      version=version,
      description="A view to edit comments created with plone.app.discussion",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='discussion edit comments',
      author='Mikel Larreategi',
      author_email='mlarreategi@codesyntax.com',
      url='http://github.com/codesyntax/cs.commenteditor',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['cs'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'plone.app.discussion'
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
