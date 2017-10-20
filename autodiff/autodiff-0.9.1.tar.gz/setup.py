from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np


setup(
    name = 'autodiff',

    version = "0.9.1",

    long_description = "A simple framework for doing automatical differentiation",
    url = "https://github.com/jeppe742/AutoDiff",
    author = "Jeppe Johan Waarkjaer Olsen",

    packages =['autodiff'],

    ext_modules = cythonize("autodiff/AdFloat.pyx"), 
    #ext_modules = [Extension('autodiff/AdFloat',['autodiff/AdFloat.c'])],
    include_dirs = [np.get_include()]

)