#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='jismesh',
      packages=['jismesh'],
      version='1.1.1',
      author='Haruki Nishikawa',
      author_email='harukinishikawa84@hotmail.com',
      url='https://github.com/hni14/jismesh',
      download_url='https://github.com/hni14/jismesh',
      keywords = ['mesh'],
      description='Utilities for area mesh code defined in Japanese Industorial Standards (JIS X 0410 地域メッシュコード).',
      license = 'MIT',
      extras_require={
         ':python_version < "3.0"': [
            'functools32',
         ],
      },
      classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        ],
     )
