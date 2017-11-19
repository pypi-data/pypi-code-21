import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='pygenderbr',
      version='0.5.0',
      description='Python tool to interface with "Nomes" IBGE API v.2',
      url='https://github.com/alexfurtunatoifrn/pygenderbr',
      author='Alex Furtunato',
      author_email='alexfurtunato@gmail.com',
      license='MIT',
      packages=['pygenderbr'],
      install_requires=[
          'pbr>=1.8',
          'requests',
          'pandas',
      ],
      long_description=read('README.rst'),
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Topic :: Software Development :: Build Tools",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: Scientific/Engineering",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 3",
      ],
      keywords='gender names brazil ibge',
      zip_safe=False)
