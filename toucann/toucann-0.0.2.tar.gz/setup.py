from setuptools import setup, find_packages
from os.path import join, dirname

import toucann

setup(
    name='toucann',
    version=toucann.__version__,
    packages=find_packages(),
    setup_requires=['matplotlib>=1.5.1', 'numpy>=1.11.1'],
    install_requires=['matplotlib>=1.5.1', 'numpy>=1.11.1'],
)
