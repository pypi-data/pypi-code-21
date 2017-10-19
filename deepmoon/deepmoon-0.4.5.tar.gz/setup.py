#!/usr/bin/env python

from setuptools import setup

install_requires = [
    'colorama',
    'dataset',
    'requests[security]',
    'tqdm >= 4.19.4'
]

setup(name="deepmoon",
      version="0.4.5",
      author="Paul Fitzpatrick",
      author_email="paulfitz@alum.mit.edu",
      description="The deep learning framework from beyond the moon",
      packages=['deepmoon'],
      entry_points={
          "console_scripts": [
              "deepmoon=deepmoon.main:main"
          ]
      },
      install_requires=install_requires,
      extras_require={
      },
      tests_require=[
      ],
      test_suite="nose.collector",
      url="https://github.com/paulfitz/deepmoon"
)
