from setuptools import setup, find_packages 
import os

os.system('rm -rf dist')

setup(name='excelmustdie',
version='0.3',
description='A MIPT lab report creation tool',
long_description='A workaround to use jupyter instead of excel + tex for MIPT laboratory reports creation',
classifiers=[ 'License :: OSI Approved :: MIT License',
'Programming Language :: Python :: 3.6',
],
keywords='MIPT tex excel',
author='Andrei Pago',
author_email='andpago@gmail.com',
license='MIT',
packages=['excelmustdie'],
install_requires=['jupyter'],
include_package_data=True,
zip_safe=False) 
