#!/usr/bin/env python
import os
import glob
from setuptools import setup, Extension
# from pynclose import gen_finclose, gen_inclose
from inclose_package import gen_inclose


MODULE_INCLOSE = 'build/inclose-binding.cpp'


inclose = Extension('inclose',
                    # sources=[module_inclose],
                    sources=[MODULE_INCLOSE, *glob.glob('inclose_package/*.cpp')],
                    include_dirs=['inclose_package/'],
                    extra_compile_args=['-fopenmp', '-O2'],
                    extra_link_args=['-fopenmp', '-O2', '-Wl,-z,defs', '-flto'],
                    language='c++')

setup(ext_modules=[inclose], packages=['pynclose'])
