# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os


version = '0.2.1'

here = os.path.abspath(os.path.dirname(__file__))

def read_file(*pathes):
    path = os.path.join(here, *pathes)
    if os.path.isfile(path):
        with open(path, 'r') as desc_file:
            return desc_file.read()
    else:
        return ''

desc_files = (('README.rst',), ('docs', 'CHANGES.rst'),
                ('docs', 'CONTRIBUTORS.rst'))

long_description = '\n\n'.join([read_file(*pathes) for pathes in desc_files])

install_requires=['setuptools']


setup(name='openmairie.devtools',
      version=version,
      description="openMairie Developer Tools",
      long_description=long_description,
      platforms = ["any"],
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        ],
      keywords="openMairie",
      author="openMairie",
      author_email="contact@openmairie.org",
      url="https://github.com/openmairie/openmairie.devtools/",
      license="GPL",
      packages=find_packages("src"),
      package_dir = {"": "src"},
      namespace_packages=["openmairie"],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      entry_points={
        'console_scripts': [
            'om-tests = openmairie.devtools.omtests:main',
            'om-svnexternals = openmairie.devtools.omsvnexternals:main',
          ],
        },
      )

# vim:set et sts=4 ts=4 tw=80:
