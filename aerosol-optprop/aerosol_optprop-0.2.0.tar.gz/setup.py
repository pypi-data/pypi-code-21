# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='aerosol_optprop',
    version='0.2.0',
    description='Optical property calculations of aerosol aerosol_optprop',
    author='Landon Rieger',
    author_email='landon.rieger@canada.ca',
    url='https://gitlab.com/LandonRieger/aerosol_optprop',
    license='MIT',
    packages=find_packages(),
    package_data={'aerosol_optprop': ['data/refractive_index']},
    include_package_data=True,
    install_requires=['numpy', 'miepython']
)