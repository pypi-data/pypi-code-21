from setuptools import setup, find_packages

from os.path import join, dirname, realpath, relpath, splitext, relpath
from os import walk, sep

import numpy as np

try:
    from Cython.Distutils.extension import Extension
    from Cython.Distutils           import build_ext as cython_build_ext
    use_cython = True
except ImportError:
    from distutils.extension import Extension
    use_cython = False

SCRIPT_DIR = dirname(realpath(__file__))
GLOVE_SOURCE_DIR  = join(SCRIPT_DIR, "glove")
GLOVE_MODULE_NAME = "glove"

def strict_lstrip(string, ending):
    if string.endswith(ending):
        return string[:-len(ending)]
    return string

def path_to_module_name(path):
    relative_path = relpath(path, SCRIPT_DIR)
    path_no_ext, _ = splitext(relative_path)
    return strict_lstrip(path_no_ext, sep).replace(sep, '.')


def find_files_by_suffix(path, suffix):
    """Recursively find files with specific suffix in a directory"""
    for relative_path, dirs, files in walk(path):
        for fname in files:
            if fname.endswith(suffix):
                yield join(path, relative_path, fname)

ext_modules = []
for pyx_file in find_files_by_suffix(GLOVE_SOURCE_DIR, ".pyx"):
    ext_modules.append(Extension(
        name=path_to_module_name(pyx_file),
        sources=[pyx_file if use_cython else pyx_file.replace(".pyx", ".cpp")],
        library_dirs=[],
        language='c++',
        extra_compile_args=['-std=c++11', '-Wno-unused-function',
                            '-Wno-sign-compare', '-Wno-unused-local-typedef',
                            '-Wno-undefined-bool-conversion', '-O3',
                            '-Wno-reorder'],
        extra_link_args=[],
        libraries=[],
        extra_objects=[],
        include_dirs=[np.get_include()]
    ))

def readfile(fname):
    return open(join(dirname(__file__), fname)).read()

cmdclass = {}
if use_cython:
    cmdclass['build_ext'] = cython_build_ext
setup(
    name=GLOVE_MODULE_NAME,
    version='1.0.2',
    cmdclass=cmdclass,
    description='Python package for computing embeddings from co-occurence matrices',
    long_description=readfile('README.md'),
    ext_modules=ext_modules,
    packages=find_packages(),
    py_modules = [],
    author='Jonathan Raiman',
    author_email='jonathanraiman@gmail.com',
    url='https://github.com/JonathanRaiman/glove',
    download_url='https://github.com/JonathanRaiman/glove',
    keywords='NLP, Machine Learning',
    license='MIT',
    platforms='any',
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.3'
    ],
    setup_requires = [],
    install_requires=['numpy'],
    include_package_data=True,
)
