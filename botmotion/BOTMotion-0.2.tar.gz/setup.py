from setuptools import setup
from os import path

import os
long_description = 'Add a fallback short description here'
if os.path.exists('README.txt'):
    long_description = open('README.txt').read()

setup(name='BOTMotion',
      version='0.2',
      description='A python module to control Synapticon BOT Motion Axis',
      long_description=long_description,
      url='https://github.com/synapticon',
      author='Synapticon GmbH',
      author_email='support@synapticon.com',
      license='LICENSE.txt',
      packages=['botmotion'],
      install_requires=['netifaces', ],

      classifiers=[
            # How mature is this project? Common values are
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 4 - Beta',

            'Programming Language :: Python :: 2.7',
      ],

      keywords='motion control cia402 canopen',

      zip_safe=False)
