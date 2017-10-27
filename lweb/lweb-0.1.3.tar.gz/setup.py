#coding: utf-8
from setuptools import setup, find_packages

__version__ = '0.1.3'

setup(
    name         = "lweb",
    version      = __version__,
    keywords     = ['web framework'],
    author       = "zii",
    author_email = "gamcat@gmail.com",
    url          = "https://github.com/zii/lweb",
    description  = "A light-weight python web framework, shameless copy from bottle.",
    long_description = open('README.rst').read(),
    license      = "MIT",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    install_requires = [],
    packages = find_packages(),
)