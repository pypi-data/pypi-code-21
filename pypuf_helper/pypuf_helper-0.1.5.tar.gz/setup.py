# This is the setup file for the pypuf_helper module

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

pypuf_helper = Extension(
  'pypuf_helper',
  include_dirs=[
    'pypuf_helper_src/include',
    ],
  sources=[
    'pypuf_helper_src/python_wrapper.c',
    'pypuf_helper_src/eval_id_xor.c',
    'pypuf_helper_src/eval.c',
    'pypuf_helper_src/eval_sign.c',
    'pypuf_helper_src/transform_id.c',
    'pypuf_helper_src/combiner_xor.c'
  ],
)

setup(name='pypuf_helper',
      packages=['pypuf_helper_src'],
      version='0.1.5',
      description='Helper module for the pypuf learning framework.',
      author='Tudor Soroceanu',
      author_email='tudor200@zedat.fu-berlin.de',
      url='https://github.com/taudor/pypuf_helper',
      download_url='https://github.com/taudor/pypuf_helper/archive/0.1.5.tar.gz',
      keywords=['pypuf PUF'],
      classifiers = [],
      cmdclass={'build_ext':build_ext},
      setup_requires = ['numpy'],
      install_requires = ['numpy'],
      ext_modules=[pypuf_helper])
