#!/usr/bin/env python
# Time-stamp: <2017-11-06 15:42:00 Hongbo Liu>

"""Description: SMART setup

Copyright (c) 2017 Hongbo Liu <hongbo919@gmail.com>

This code is free software; you can redistribute it and/or modify it
under the terms of the BSD License (see the file COPYING included
with the distribution).

@status: release candidate
@version: 2.2.4
@author:  Hongbo Liu
@contact: hongbo919@gmail.com
"""

# ------------------------------------
# python modules
#/Users/hongbo.liu/Documents/HongboData/Programming/Code/PyDev/Pythonworkspace/SMART
# Make pacage in Linux system
# python setup.py sdist bdist_wheel
# twine upload dist/SMART_BS_Seq-2.2.4-py2-none-any.whl dist/SMART-BS-Seq-2.2.4.tar.gz
# ------------------------------------
#from distutils.core import setup
from setuptools import setup
import sys
# Use build_ext from Cython if found
command_classes = {}

def main():
    if float(sys.version[:3])<2.7 or float(sys.version[:3])>=2.8:
        sys.stderr.write("CRITICAL: Python version must be 2.7!\n")
        sys.exit(1)
    
    setup(name="SMART-BS-Seq",
          version="2.2.4",
          description="Specific Methylation Analysis and Report Tool 2",
          long_description=open('README.rst', 'rt').read(),
          author='Hongbo Liu',
          author_email='hongbo919@gmail.com',
          url='http://fame.edbc.org/smart/',
          package_dir={'SMART' : 'SMART'},
          packages=['SMART'],
          package_data={'SMART':['Example/MethylMatrix_Test.txt','Example/CpGisland_hg19.bed']},
          #py_modules = ['Splitchrome','MethyMergeEntropy','SegmentationNormal','Folderprocess','NewEntropy','NewEntropyNormal'],    
          scripts=['bin/SMART'],
          classifiers=[
              'Development Status :: 5 - Production/Stable',
              'Programming Language :: Python',
              'License :: OSI Approved :: Python Software Foundation License',
              'Intended Audience :: End Users/Desktop',
              'Operating System :: POSIX :: Linux',
              'Operating System :: MacOS',
              ],
          install_requires=['scipy>=0.18.1','numpy>=1.11.2','statsmodels>=0.8.0','pandas==0.19.2'],
          cmdclass = command_classes
          #install_requires=['scipy>=0.13',#],
          )


if __name__ == '__main__':
    main()
