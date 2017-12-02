from distutils.core import setup
from setuptools import find_packages


setup(name='tfoutputs',
version='0.0.2',
description='A library to get your terraform outputs in your python code',
license='MIT',
url='https://github.com/jae2/python-tfoutputs',
long_description="A library to get your terraform outputs in your python code'",
install_requires=['boto3'],
packages=find_packages(exclude=['contrib', 'docs', 'test*','venv*','build','dist','.cache','fixtures','.cache']),
author_email='admin@jaetech.org',
author='James Edwards',
classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Intended Audience :: Information Technology',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
]
)
