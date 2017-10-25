
# coding: utf-8

# In[ ]:


import os
from os.path import join, dirname
from setuptools import setup, find_packages

def read(fname):
    return open(join(dirname(__file__), fname)).read()

setup(
    name = "pytorchbp",
    version = "0.0.15",
    author = "John Prothero",
    author_email = "john.s.prothero@gmail.com",
    description = "Pytorch Boilerplate Code",
    license = "MIT",
    keywords = "pytorch boiler plate boilerplate",
    url = "https://github.com/jprothero/pytorchbp",
    packages = find_packages(),
    long_description = read('README'),
    classifiers = [],
)

