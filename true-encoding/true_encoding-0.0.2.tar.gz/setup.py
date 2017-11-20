#coding:utf-8

from distutils.core import setup
from setuptools import find_packages


PACKAGE = "true_encoding"
NAME = "true_encoding"
DESCRIPTION = "true_encoding is the method of solving the problem of 'ISO-8859-1'."
AUTHOR = "UlionTse"
AUTHOR_EMAIL = "shinalone@outlook.com"
URL = "https://github.com/shinalone/true_encoding"
VERSION = __import__(PACKAGE).__version__

with open('README.rst','r',encoding='utf-8') as file:
    long_description = file.read()

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="MIT",
    url=URL,
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6"
    ],
    keywords=['encoding','true_encoding'],
    install_requires=[],
    zip_safe=False,
)