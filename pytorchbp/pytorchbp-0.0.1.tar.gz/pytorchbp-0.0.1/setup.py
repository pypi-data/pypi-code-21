
# coding: utf-8

# In[ ]:


import os
from os.path import join, dirname
from setuptools import setup

def read(fname):
    return open(join(dirname(__file__), fname)).read()

setup(
    name = "pytorchbp",
    version = "0.0.1",
    author = "John Prothero",
    author_email = "john.s.prothero@gmail.com",
    description = "Pytorch Boilerplate Code",
    license = "MIT",
    keywords = "pytorch boiler plate boilerplate",
    url = "http://packages.python.org/pytorchbp",
    packages = ['pytorchbp'],
    long_description = read('README'),
#    classifiers = [
#        "Development Status :: 2 - Pre-Alpha",
#        "Topic :: Utilities",
 #       "License :: MIT License",
 #   ],
)

