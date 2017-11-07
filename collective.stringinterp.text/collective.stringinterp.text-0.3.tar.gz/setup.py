from setuptools import setup, find_packages
import os

version = '0.3'

tests_require = ['plone.app.testing', 'plone.dexterity']

setup(name='collective.stringinterp.text',
      version=version,
      description="Additional string interpolation for Plone: add content text in "
                  "your contentrule e-mail messages",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Plone",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        ],
      keywords='plone plonegov rule interpolation email',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.it',
      url='http://plone.org/products/collective.stringinterp.text',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.stringinterp'],
      include_package_data=True,
      zip_safe=False,
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      install_requires=[
          'setuptools',
          'plone.stringinterp',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
