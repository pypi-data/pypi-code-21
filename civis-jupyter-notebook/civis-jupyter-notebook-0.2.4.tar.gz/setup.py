import os
from setuptools import find_packages, setup


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as _in:
        return _in.read()


__version__ = None
exec(read('civis_jupyter_notebooks/version.py'))

setup(
    name="civis-jupyter-notebook",
    version=__version__,
    author="Civis Analytics Inc",
    author_email="opensource@civisanalytics.com",
    url="https://www.civisanalytics.com",
    description=("A tool for building Docker images for Civis "
                 "Platform Jupyter notebooks."),
    packages=find_packages(),
    long_description=read('README.rst'),
    include_package_data=True,
    license="BSD-3",
    install_requires=read('requirements.txt').strip().split('\n'),
    scripts=['civis_jupyter_notebooks/assets/civis-jupyter-notebooks-start'],
    entry_points={
        'console_scripts': [
            'civis-jupyter-notebooks-install = '
            'civis_jupyter_notebooks.__main__:cli',
            ]})
