import glob
import os
from distutils.command.build_clib import build_clib
from distutils.command.build_ext import build_ext as _du_build_ext
from setuptools.command.install import install
from distutils.core import setup,  Extension

try:
    # Attempt to use Cython for building extensions, if available
    from Cython.Distutils.build_ext import build_ext as build_ext
except ImportError:
    build_ext = _du_build_ext


# Source locations
src_loc = os.path.join('ART',
                       'source')
inc_loc = os.path.join('ART',
                       'include')
artpy_src = glob.glob(os.path.join('*.lds'))
artpy_src = glob.glob(os.path.join('artpy', '*'))
art_src = glob.glob(os.path.join(src_loc, 'art', '*.cpp'))
art_inc = [os.path.join(inc_loc, 'art')]

muparser_src = glob.glob(os.path.join(src_loc, 'muParser', '*.cpp'))
muparser_inc = [os.path.join(inc_loc, 'muParser')]

ga_src = glob.glob(os.path.join(src_loc, 'ga', '*.cpp'))
ga_inc = [os.path.join(inc_loc, 'ga')]

fortran_src = glob.glob(os.path.join(src_loc, 'fortran', '*.c*'))
fortran_inc = [os.path.join(inc_loc, 'fortran')]
# Includes location
src_base = [os.path.join('ART', 'source')] + \
           glob.glob(os.path.join('ART', 'source'))

inc_base = src_base + [os.path.join('ART', 'include')] + \
           glob.glob(os.path.join('ART',
                                  'include', '*'))


libmuparser = ('muparser', {'sources': muparser_src,
                            'include_dirs': inc_base+muparser_inc})
libga = ('ga', {'sources': ga_src,
                'include_dirs': inc_base+ga_inc})
libfortran = ('fortran', {'sources': fortran_src,
                          'include_dirs': fortran_inc})
libart = ('art', {'sources': art_src,
                  'include_dirs': inc_base + src_base + art_inc})
artext = [Extension('artoolpy.artsim',  # art_src,
                    define_macros=[('MAJOR_VERSION', '1'),
                                   ('MINOR_VERSION', '0')],
                    sources=art_src+art_inc,
                    include_dirs=inc_base,
                    library_dirs=inc_base,
                    extra_compile_args=['-shared', '-Wall',
                                        '-fPIC',  '-fpermissive',
                                        '-std=c++98', '-Wextra'],
                    extra_link_args=['-shared', '-Xlinker', 'tokens.lds'])]

setup(name='artoolpy',
      version='1.02',
      platforms=['linux', 'windows'],
      description='Initial version',
      author='Gytha Ogg',
      author_email='gythaoggscat@gmail.com',
      url='https://gythaogg.github.io',
      long_description='''Python wrapper for ARTool (artool.sourceforge.net)
      ''',
      cmdclass={'build_clib': build_clib,
                'build_ext': build_ext,
                'install': install},
      license='MIT',
      ext_modules=artext,
      libraries=[libart, libfortran, libmuparser, libga],
      # library_dirs=inc_base,
      py_modules=['artoolpy.artsimdefs'],
      packages=['artoolpy'],
      package_data={'artoolpy': [os.path.join('artoolpy', '*'),
                                 'tokens.lds']},
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'numpy',
          'scipy',
          'matplotlib',
          # ctypes
          'Cython',
          # 'twine',
          # 'wheel',
          # 'auditwheel'
      ],
      classifiers=[
          # How mature is this project? Common values are
          #   3 - Alpha
          #   4 - Beta
          #   5 - Production/Stable
          'Development Status :: 3 - Alpha',
          # Indicate who your project is intended for
          # 'Intended Audience :: Scientists',
          'Topic :: Software Development :: Build Tools',
          # Pick your license as you wish (should match "license" above)
          'License :: OSI Approved :: MIT License',
          # Specify the Python versions you support here. In particular, ensure
          # that you indicate whether you support Python 2, Python 3 or both.
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3'])
