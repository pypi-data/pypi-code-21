# This is the setup file for the amazing Xun module

from setuptools import setup
from setuptools.extension import Extension

if __name__ == "__main__":
    ext_modules = [ Extension('xun', 
                              ['src/xun.cpp'],
                              include_dirs = [],
                              # Extra symbols for compiler
                              extra_compile_args = ['-g', '-std=c++11'],
                              # Extra symbols for the linker
                              extra_link_args = ['-g']
                          )
                ]
    
    setup(
        name='xun',
        version = "1.0.0",
        license = "COPYING.LESSER",
        description = "The amazing Xun module",
        long_description=open("README.rst").read(),
        url="",
        author = "Xun",
        author_email = "xun@sandia",
        ext_modules = ext_modules,
        include_dirs=[],
        install_requires=['numpy'],
        zip_safe = False
    )

