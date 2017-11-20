#!/usr/bin/env python
import os
import glob
from setuptools import setup, Extension
# from pynclose import gen_finclose, gen_inclose
from inclose_package import gen_inclose

module_inclose = 'build/inclose-binding.cpp'
# with open(module_inclose, 'w') as file_:
    # print('Generating file {}'.format(module_inclose))
    # gen_inclose.generate(file_)

inclose = Extension('inclose',
                    # sources=[module_inclose],
                    sources=[module_inclose, *glob.glob('inclose_package/*.cpp')],
                    include_dirs=['inclose_package/'],
                    extra_compile_args=['-fopenmp', '-O2'],
                    extra_link_args=['-fopenmp', '-O2', '-Wl,-z,defs', '-flto'],
                    language='c++')

setup(ext_modules=[inclose], packages=['pynclose'])
