import sys, os, imp
from setuptools import Extension

dirname = os.path.dirname(__file__)
path_version = os.path.join(dirname, "../vaex/version.py")
version = imp.load_source('version', path_version)

name        = 'vaex'
author      = "Maarten A. Breddels",
author_email= "maartenbreddels@gmail.com",
license     = 'MIT'
version     = version.versionstring
url         = 'https://www.github.com/maartenbreddels/vaex'
# TODO: can we do without requests and progressbar2?
# TODO: after python2 supports frops, future and futures can also be dropped
# TODO: would be nice to have astropy only as dep in vaex-astro
install_requires_core = ["numpy>=1.11", "scipy", "astropy>=1", "aplus", "futures>=2.2.0",
    "future>=0.15.2", "pyyaml", "progressbar2", "psutil>=1.2.1", "requests", "six"]
install_requires_viz = ["matplotlib>=1.3.1", ]
install_requires_server = ["tornado>4.1", "cachetools"]
install_requires_astro = ["kapteyn"]

packages = ["vaex"]

class get_numpy_include(object):
    """Helper class to determine the numpy include path
    The purpose of this class is to postpone importing numpy
    until it is actually installed, so that the ``get_include()``
    method can be invoked. """

    def __init__(self):
        pass

    def __str__(self):
        import numpy as np
        return np.get_include()

extra_compile_args = ["-std=c++0x", "-mfpmath=sse", "-O3", "-funroll-loops"]

extension_vaexfast = Extension("vaex.vaexfast", [os.path.join(dirname, "../src/vaex/vaexfast.cpp")],
                include_dirs=[get_numpy_include()],
                extra_compile_args=extra_compile_args)
