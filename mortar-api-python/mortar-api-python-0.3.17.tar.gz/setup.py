try:
    from setuptools import setup
except:
    from distutils.core import setup

from distutils.core import setup

setup(name='mortar-api-python',
      version='0.3.17',
      description='Python API for Mortar',
      long_description='Python API client for interacting with Mortar',
      author='Mortar Data',
      author_email='info@mortardata.com',
      url='http://github.com/mortardata/mortar-api-python',
      namespace_packages = [
        'mortar'
      ],
      packages=[
          'mortar.api',
          'mortar.api.v2'
      ],
      license='LICENSE.txt',
      install_requires=[
          'requests'
      ],
      test_suite="nose.collector",
      tests_require=[
          'mock',
          'nose>=1.3.0',
          'unittest2'
      ]
)
