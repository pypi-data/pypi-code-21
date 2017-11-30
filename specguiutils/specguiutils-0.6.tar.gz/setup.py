'''
 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.
'''
from setuptools import setup
from setuptools import find_packages
PACKAGE_NAME = 'specguiutils'
setup(name=PACKAGE_NAME,


      version='0.6',
      description='Library to provide PyQt5 widgets to display spec file information read using ' +
                   'spec2nexus.spec file library',
      author = 'John Hammonds',
      author_email = 'JPHammonds@anl.gov',
      url = '',
      packages = find_packages(exclude=["*.test", "*.test.*", "test.*", "test"]),
      license = 'See LICENSE File',
      platforms = 'any',
      install_requires = ['spec2nexus >= 2017.901.4',],
      #          Also requires pyqt>= 5.6  cannot get this from pip.  Do conda install pyqt if using anaconda
      python_requires = ">=3.5, <4",

)