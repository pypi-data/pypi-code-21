# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""resswitch: GUI for analyzing resistive switching data

Useful for analyzing experiments involving memristor
transport measurements.

"""

from setuptools import setup

description = 'Useful for analyzing experiments involving memristor '
description += 'transport measurements.'

setup(name='resswitch',
      version='0.1.4',
      description='GUI for analyzing resistive switching data',
      long_description=description,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Topic :: Scientific/Engineering :: Physics',
      ],
      url='https://github.com/danieljosesilva/resswitch',
      author='Daniel Silva',
      author_email='djsilva99@gmail.com',
      license='MIT',
      packages=['resswitch'],
      install_requires=[
          'matplotlib',
          'numpy'
      ],
      scripts=['bin/resswitch'],
      include_package_data=True,
      zip_safe=False)
