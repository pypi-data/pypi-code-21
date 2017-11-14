# This is the setup file for the polymathmodule.c extension

from setuptools import setup
from setuptools.extension import Extension
from setuptools.command.build_ext import build_ext as _build_ext

# solution from https://stackoverflow.com/a/21621689
class build_ext(_build_ext):
    def finalize_options(self):
        _build_ext.finalize_options(self)
        __builtins__.__NUMPY_SETUP__ = False
        import numpy
        self.include_dirs.append(numpy.get_include())

polymath = Extension('polymath',
                    include_dirs=['./polymath_src/polymath_c'],
                    sources=['polymath_src/python_wrapper.c',
                             'polymath_src/polymath_c/poly_array_to_uint8.c',
                             'polymath_src/polymath_c/uint8_to_poly_array.c',
                             'polymath_src/polymath_c/shift_lfsr.c',
                             'polymath_src/polymath_c/polynomial_multiplication.c',
                             'polymath_src/polymath_c/polynomial_modulo_padding.c',
                             'polymath_src/polymath_c/polynomial_modulo.c',
                             ],
                     )

setup(name='polymath',
      packages=['polymath_src'],
      version='0.1.18',
      description='Lightweight and fast implementation of polynomial operations over GF(2).',
      author='Tudor Soroceanu',
      author_email='tudor200@zedat.fu-berlin.de',
      url='https://github.com/taudor/polymath',
      download_url='https://github.com/taudor/polymath/archive/0.1.18.tar.gz',
      keywords=['polynomials','LFSR','GF(2)'],
      classifiers = [],
      cmdclass={'build_ext':build_ext},
      setup_requires = ['numpy'],
      install_requires = ['numpy'],
      ext_modules=[polymath])
