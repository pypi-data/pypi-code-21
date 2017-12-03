#!/usr/bin/python
from setuptools import setup

with open('README.rst') as file:
    long_description = file.read()

setup(name='Radiovy',
      version='1.0.1',
      description='Internet radio player on kivy GUI',
      long_description=long_description,
      author='Shiro Ninomiya',
      author_email='shiro@snino.com',
      license="GPL3",
      packages=['hkbase', 'getradiourl', 'radiovy'],
      install_requires=['kivy >= 1.10.0', 'ZODB', 'pgi'],
      entry_points = {
          'console_scripts' : ['radiovy = radiovy.radiovy:main']
      },
      package_data = {
          'hkbase' : [ '*.png','config.cfg' ],
          'radiovy' : [ 'files/*.png' ],
      },
      
)
