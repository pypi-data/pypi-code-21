from setuptools import setup, find_packages
from daon import __version__

setup(name='daon',
      version=__version__,
      description='Daon Korean Analyzer',
      url='http://github.com/rasoio/daon-python',
      author='rasoio',
      author_email='rasoio@naver.com',
      license='MIT',
      install_requires=['py4j'],
      packages=find_packages(exclude=['contrib', 'docs', 'tests']),
      package_data={'daon':['java/daonCore.jar']},
      zip_safe=False)
