"""
The Good Library

The Good Library is a collection of programming and syntax tools that makes your
python code more expressive and easier to work with.

Author:  Anshul Kharbanda
Created: 10 - 6 - 2017
"""
from distutils.core import setup

# Setup function
setup(name='good-library',
      version='0.3-beta.0',
      description='A collection of programming and syntax tools for experienced Python users',
      author='Anshul Kharbanda',
      author_email='akanshul97@gmail.com',
      url='https://www.github.org/andydevs/good-library',
      packages=['good', 'good.handlers'])
