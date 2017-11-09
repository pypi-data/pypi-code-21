#!/usr/bin/python


try:
    from Cython.Build import cythonize
except ImportError:
    print('install cython first')
try:
    import numpy as np
except ImportError:
    print('install numpy first')
from setuptools import Extension, find_packages, setup

description = (
        'This repository contains scripts for'
        'inspection, preparation, and evaluation of the Cityscapes dataset.')

extensions = [Extension(
        'cityscapesscripts.evaluation.addToConfusionMatrix',
        ["cityscapesscripts/evaluation/addToConfusionMatrix.pyx"],
        include_dirs=[np.get_include()])]
setup(
        name='cityscapesScripts',
        version='1.0.0',
        description=description,
        url='https://github.com/mcordts/cityscapesScripts',
        author='mcordts',
        license='custon',

        packages=find_packages(),
        install_requires=['numpy', 'pillow', 'matplotlib'],
        setup_requires=['setuptools>=18.0', 'cython', 'numpy'],
        ext_modules=cythonize(extensions),
)
