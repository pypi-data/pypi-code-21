# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='jupyter_erp5_storage',
    version='0.0.1',
    packages=['jiocontents'],
    package_data = {
        '': ['*.js', '*.html']
    },

    # PyPI Data
    author='Sebastian Kreisel',
    author_email='sebastian.kreisel@nexedi.com',
    description='ERP5 Storage for jupyter',
    keywords='renderjs erp5 storage jupyter nbextension',
    license='GPL 2',
    url='https://lab.nexedi.com/Kreisel/jupyter-renderjs'
)
