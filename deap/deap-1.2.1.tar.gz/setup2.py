import sys
import warnings

from setuptools import setup, find_packages, Extension

import deap

try:
    from pypandoc import convert
except ImportError:
    warnings.warn("warning: pypandoc module not found, could not convert ReadMe Markdown to RST")
    import codecs
    read_md = lambda f: codecs.open(f, 'r', 'utf-8').read()
else:
    read_md = lambda f: convert(f, 'rst')

hv_module = Extension("deap.tools._hypervolume.hv", sources=["deap/tools/_hypervolume/_hv.c", "deap/tools/_hypervolume/hv.cpp"], optional=True)

setup(name='deap',
      version=deap.__revision__,
      description='Distributed Evolutionary Algorithms in Python',
      long_description=read_md('README.md'),
      author='deap Development Team',
      author_email='deap-users@googlegroups.com',
      url='https://www.github.com/deap',
    #   packages=['deap', 'deap.tools', 'deap.tools._hypervolume', 'deap.benchmarks', 'deap.tests'],
      packages=find_packages(exclude=['examples']),
      platforms=['any'],
      keywords=['evolutionary algorithms','genetic algorithms','genetic programming','cma-es','ga','gp','es','pso'],
      license='LGPL',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Intended Audience :: Education',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Topic :: Scientific/Engineering',
          'Topic :: Software Development',
      ],
      ext_modules = [hv_module],
      use_2to3=True
)