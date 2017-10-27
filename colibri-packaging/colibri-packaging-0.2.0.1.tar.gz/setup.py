# coding: utf-8
from setuptools import setup
from versao import version_info


setup(
    name='colibri-packaging',
    author='Colibri Agile',
    author_email='colibri.agile@gmail.com',
    platforms=['Windows'],
    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html'
    version=version_info()['fileversion'],
    description='Colibri Master Packages generator',
    packages=[
        'colibri_packaging'
    ],
    package_data={
        'colibri_packaging': ['7za.exe']
    },
    data_files=[('', ['versao.py', '__version__.py', '__buildnumber__.py'])],
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    python_requires='>=2.7,!=3.0.*,!=3.1.*'
)
