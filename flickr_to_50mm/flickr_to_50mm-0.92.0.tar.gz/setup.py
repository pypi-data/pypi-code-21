
"""
A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

setup(
  name = 'flickr_to_50mm',
  packages = ['flickr_to_50mm'], # this must be the same as the name above
  version = '0.92.0',
  description = 'Configuration generator for 50mm from flickr photosets',
  author = 'Ara Hayrabedian',
  author_email = 'flickr_to_50mm.pypi@hyrbdn.com',
  url = 'https://github.com/arahayrabedian/flickr_to_50mm', # use the URL to the github repo
  keywords = ['configuration', '50mm', 'flickr', 'migrate', 'migration', 'export'], # arbitrary keywords
  classifiers=[
      # How mature is this project? Common values are
      #   3 - Alpha
      #   4 - Beta
      #   5 - Production/Stable
      'Development Status :: 4 - Beta',

      # Indicate who your project is intended for
      'Intended Audience :: System Administrators',

      # Pick your license as you wish (should match "license" above)
      'License :: OSI Approved :: MIT License',

      # Specify the Python versions you support here. In particular, ensure
      # that you indicate whether you support Python 2, Python 3 or both.
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.3',
      'Programming Language :: Python :: 3.4',
      'Programming Language :: Python :: 3.5',
      'Programming Language :: Python :: 3.6',
  ],
  install_requires=['PyYAML == 3.12',
                    'requests == 2.18.4'],
  entry_points={
        'console_scripts': [
            'flickr_to_50mm=flickr_to_50mm.flickr_to_50mm:main',
        ],
    },
)
