import os
from setuptools import setup, find_packages
from setuptools.extension import Extension

from numpy.distutils.misc_util import get_numpy_include_dirs

version = "0.0.0dev2"
basedir = os.path.dirname(os.path.realpath(__file__))

##########################
# SPGLib Extension module
spglib_include_dir = os.path.join(basedir, 'quantipy/spglib/src/')
spglib_sources = [os.path.join(spglib_include_dir, f) for f in
                  os.listdir(spglib_include_dir)
                  if os.path.splitext(f)[1] == ".c" ] +\
                     [os.path.join(basedir, 'quantipy/spglib/_spglib.c')]

spglib_extension = Extension('_spglib',
                             include_dirs = [spglib_include_dir] +
                             get_numpy_include_dirs(), 
                             sources = spglib_sources,
                             # extra_compile_args=['-fopenmp'],
                             # extra_link_args=['-lgomp'],
                         )

##########################
# quicked Extension module
quicked_include_dir = os.path.join(basedir, 'quantipy/quicked/src/')
quicked_sources = [os.path.join(quicked_include_dir, f) for f in
                  os.listdir(quicked_include_dir)
                  if os.path.splitext(f)[1] == ".cpp" ] +\
                     [os.path.join(basedir, 'quantipy/quicked/_quicked.cpp')]

quicked_extension = Extension('_quicked',
                             include_dirs = [quicked_include_dir] +
                              [os.path.join(quicked_include_dir, x[0]) \
                               for x in os.walk(quicked_include_dir)] +
                              get_numpy_include_dirs(), 
                             sources = quicked_sources,
                             # extra_compile_args=['-fopenmp'],
                             # extra_link_args=['-lgomp'],
                         )

setup(
    name = "QuantiPy",
    version = version,
    description = "Python Framework for Quantum Many-Body Computations",
    author = "Alexander Wietek, Michael Schuler",
    author_email = "alexander.wietek@uibk.ac.at",
    packages = find_packages(exclude=['demo', 'docs', 'tests*']),
    license="GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007",
    ext_modules = [quicked_extension, spglib_extension],
    setup_requires=['pytest-runner'],
    tests_require=['pytest']
)
