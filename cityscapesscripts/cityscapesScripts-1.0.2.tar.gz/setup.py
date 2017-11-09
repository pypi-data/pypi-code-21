#!/usr/bin/python


try:
    import numpy as np
except ImportError:
    print('install numpy first')
from setuptools import Extension, find_packages, setup

description = (
        'This repository contains scripts for'
        'inspection, preparation, and evaluation of the Cityscapes dataset.')
pyxfile = 'cityscapesscripts/evaluation/addToConfusionMatrix.c'
extensions = [Extension(
        'cityscapesscripts.evaluation.addToConfusionMatrix',
        [pyxfile],
        include_dirs=[np.get_include()])]
setup(
        name='cityscapesScripts',
        version='1.0.2',
        description=description,
        url='https://github.com/mcordts/cityscapesScripts',
        author='mcordts',
        license='custon',

        packages=find_packages().append(pyxfile),
        install_requires=['numpy', 'pillow', 'matplotlib'],
        setup_requires=['setuptools>=18.0', 'numpy'],
        ext_modules=extensions,
)
