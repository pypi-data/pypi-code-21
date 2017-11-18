#!/usr/bin/env python3
import os
import re
import setuptools
from typing import Dict


here = os.path.abspath(os.path.dirname(__file__))


def get_meta() -> Dict[str, str]:
    with open(os.path.join(here, 'pyramid_json_response.py')) as f:
        source = f.read()

    regex = r'^{}\s*=\s*[\'"]([^\'"]*)[\'"]'
    return lambda name: re.search(regex.format(name), source, re.MULTILINE).group(1)


get_meta = get_meta()

install_requires = []

test_requires = [
    'flake8',
    'mypy',
    'pytest',
    'pytest-cov',
]

setuptools.setup(
    name='pyramid_json_response',
    version=get_meta('__version__'),
    description="",
    long_description="",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries"
    ],
    keywords=["pyramid"],
    author=get_meta('__author__'),
    author_email=get_meta('__email__'),
    url="https://github.com/narusemotoki/pyramid_json_response",
    license=get_meta('__license__'),
    py_modules=['pyramid_json_response'],
    install_requires=install_requires,
    extras_require={
        'test': test_requires,
    },
    include_package_data=True,
)
