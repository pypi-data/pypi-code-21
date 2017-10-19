from setuptools import setup

setup(name='cplusnew',
      version='0.5',
      description='Convenience script for creating C++ projects with CMake setup',
      author='marksei',
      author_email='mark.seidenschnur@gmail.com',
      license='MIT',
      packages=['cplusnew'],
      scripts=['bin/cplusnew'],
      zip_safe=False)