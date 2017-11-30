# -*- coding: utf-8 -*-

# HACK for `nose.collector` to work on python 2.7.3 and earlier
import multiprocessing
from setuptools import setup, find_packages


install_requires = [
  'boto3 == 1.4.4',
  'poolmanager == 0.0.5',
  'configparser == 3.5.0',
  'gatilegrid == 0.1.5',
  'pyproj == 1.9.5.1',
]


setup(name=u'tool_aws',
      version=u'0.0.6',
      description=u'AWS scripts for geoadmin',
      author=u'Andrea Borghi, Loic Gasser',
      author_email=u'andrea.borghi@swisstopo.ch, loicgasser4@gmail.com',
      license=u'BSD-2',
      url=u'https://github.com/geoadmin/tool-aws.git',
      packages=find_packages(exclude=['tests']),
      zip_safe=False,
      test_suite='nose.collector',
      install_requires=install_requires,
      entry_points={
          'console_scripts': [
              's3rm=tool_aws.s3.rm:main',
          ]
      },
      )
