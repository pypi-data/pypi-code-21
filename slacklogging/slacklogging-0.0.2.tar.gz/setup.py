#!/usr/bin/env python3
import os
import re

import setuptools

here = os.path.abspath(os.path.dirname(__file__))


def get_meta() -> str:
    with open(os.path.join(here, 'slacklogging.py')) as f:
        source = f.read()

    regex = r"^{}\s*=\s*['\"]([^'\"]*)['\"]"
    return lambda name: re.search(regex.format(name), source, re.MULTILINE).group(1)


get_meta = get_meta()

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

requires = [
    'requests',
]

tests_require = [
    'flake8',
    'pytest',
]

setuptools.setup(
    name='slacklogging',
    version=get_meta('__version__'),
    description="Slack logging integration.",
    long_description=README,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
    ],
    author=get_meta('__author__'),
    author_email=get_meta('__email__'),
    url="https://github.com/narusemotoki/slacklogging",
    keywords=["logging", "slack"],
    py_modules=['slacklogging'],
    extras_require={
        'testing': tests_require,
    },
    install_requires=requires,
    include_package_data=True,
    license="MIT License",
)
