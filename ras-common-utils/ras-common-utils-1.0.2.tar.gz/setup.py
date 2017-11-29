#!/usr/bin/env python
# encoding: UTF-8

import ast
import os.path

from setuptools import setup, find_packages

try:
    # For setup.py install
    from ras_common_utils.__version__ import __version__ as version
except ImportError:
    # For pip installations
    version = str(
        ast.literal_eval(
            open(os.path.join(
                os.path.dirname(__file__),
                "ras_common_utils", "__version__.py"),
                'r').read().split("=")[-1].strip()
        )
    )

install_requirements = [
    i.strip() for i in open(
        os.path.join(os.path.dirname(__file__), "requirements.txt"), 'r'
    ).readlines()
]

setup(
    name="ras-common-utils",
    version=version,
    description="A common library for RAS utilities",
    author="G Irving",
    author_email="gemma.i_95@hotmail.co.uk",
    url="https://github.com/ONSdigital/ras-common-utils",
    long_description=__doc__,
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License"
    ],
    packages=[
        "ras_common_utils",
        "ras_common_utils.ras_config",
        "ras_common_utils.ras_database",
        "ras_common_utils.ras_error",
        "ras_common_utils.ras_logger",
        "ras_common_utils.util",
    ],
    package_data={
        "ras_common_utils": [
            "requirements.txt",
        ]
    },
    install_requires=install_requirements,
    entry_points={
        "console_scripts": []
    }
)
