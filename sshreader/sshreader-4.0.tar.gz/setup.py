#!/usr/bin/env python2
# coding=utf-8
"""Setup file for sshreader module"""

from setuptools import setup

setup(name='sshreader',
      version='4.0',
      description='Multi-threading/processing wrapper for Paramiko',
      author='Jesse Almanrode',
      author_email='jesse@almanrode.com',
      url='http://sshreader.readthedocs.io/',
      packages=['sshreader'],
      include_package_data=True,
      scripts=['bin/pydsh'],
      license='GNU Lesser General Public License v3 or later (LGPLv3+)',
      install_requires=['click==6.7',
                        'colorama==0.3.9',
                        'future==0.16.0',
                        'paramiko==2.3.1',
                        'progressbar2==3.34.3',
                        'python-hostlist==1.17',
                        ],
      platforms=['Linux', 'Darwin'],
      classifiers=[
          'Programming Language :: Python',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
          'Development Status :: 5 - Production/Stable',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
      )
