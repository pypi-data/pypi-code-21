import os
from setuptools import find_packages, setup


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as _in:
        return _in.read()


__version__ = None
exec(read('civis_jupyter_ext/version.py'))

setup(
    name="civis-jupyter-extensions",
    version=__version__,
    author="Civis Analytics Inc",
    author_email="opensource@civisanalytics.com",
    url="https://www.civisanalytics.com",
    description=("Tools for using the Civis "
                 "Platform with Jupyter notebooks."),
    packages=find_packages(),
    long_description=read('README.rst'),
    include_package_data=True,
    license="BSD-3",
    install_requires=read('requirements.txt').strip().split('\n'))
