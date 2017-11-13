#from distutils.core import Extension
from setuptools import setup, Extension
import os

path_str = os.getcwd()
module1 = Extension('nolan',
					libraries = ['call'],
					library_dirs = [path_str],
					sources = ['nolan.c'])
setup (name = 'nolan',version = '0.1.0',description = 'This is module can be used to make paralle http requests.',ext_modules = [module1])
