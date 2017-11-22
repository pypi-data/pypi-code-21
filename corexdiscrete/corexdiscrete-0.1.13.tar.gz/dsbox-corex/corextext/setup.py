# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

try:
    long_description = open("README.rst").read()
except IOError:
    long_description = ""

setup(
    name="corextext",
    version="0.1.4",
    description="Return components/latent factors that explain the most multivariate mutual information in the data under Linear Gaussian model. For comparison, PCA returns components explaining the most variance in the data.",
    license="AGPL-3.0",
    author="Rob Brekelmans/Greg Ver Steeg",
    author_email="brekelma@usc.edu",
    packages=find_packages(),
    url='https://github.com/brekelma/corextext',
    download_url='https://github.com/brekelma/corextext',
    install_requires=[],
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
    ]
)
