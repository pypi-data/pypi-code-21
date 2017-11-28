from setuptools import setup, Extension

extension = Extension("_interface", sources=["_interface/pyparport.c"])

setup(name="pyparport",
      version="0.6",
      description="This module provides the possibility to connect to the first parallel port from Python.",
      license='GPLv3',
      packages=['_interface', "pyparport"],
      author='Christian Kokoska',
      author_email='christian@softcreate.de',
      ext_modules=[extension])
