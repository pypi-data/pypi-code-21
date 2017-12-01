import codecs
import os
import sys

try:
	from setuptools import setup
except:
	from distutils.core import setup



def read(fname):
	return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()

long_des = read("README.rst")
    
platforms = ['linux/Windows']
classifiers = [
    'Development Status :: 3 - Alpha',
    'Topic :: Text Processing',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
]

install_requires = [
    'numpy>=1.11.1',
    'pandas>=0.19.0'
]

    
setup(name='Pytestxj',
      version='0.6.1',
      description='A test module for DataXujing',
      long_description=long_des,
      py_modules=['pytestxu'],
      author = "DataXujing",  
      author_email = "xujing@inter-credit.net" ,
      url = "https://dataxujing.github.io" ,
      license="Apache License, Version 2.0",
      platforms=platforms,
      classifiers=classifiers,
      install_requires=install_requires
      
      )   
      
      

  