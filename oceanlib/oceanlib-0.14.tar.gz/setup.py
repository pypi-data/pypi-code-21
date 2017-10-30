from setuptools import setup, find_packages
from datetime import datetime

setup(name='oceanlib',
      version=0.14,
      description='Financial Library',
      url='https://github.com/ubersonam/ocean',
      author='Sonam Srivastava',
      author_email='sonaam1234@gmail.com',
      license='MIT',
      packages=find_packages(),
      classifiers=[ 
	    'Development Status :: 4 - Beta', 
	    'Intended Audience :: System Administrators', 
	    'License :: OSI Approved :: Apache Software License',
	    'Programming Language :: Python :: 3'
		],
      zip_safe=False)