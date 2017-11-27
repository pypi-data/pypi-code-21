#!/usr/bin/env python
from setuptools import find_packages, setup

project = "russell-cli"
version = "0.5.5"
setup(
    name=project,
    version=version,
    description="Command line tool for russell",
    author="Russell",
    author_email="support@russellcloud.cn",
    url="https://github.com/RussellCloud/russell-cli",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    keywords="russell",
    install_requires=[
        "click>=6.7",
        "requests>=2.12.4",
        "marshmallow>=2.11.1",
        "pytz>=2016.10",
        "shortuuid>=0.4.3",
        "tabulate>=0.7.7",
        "kafka-python>=1.3.3",
        "pathlib2>=2.3.0",
        "tzlocal>=1.4",
        "progressbar33>=2.4",
        "websocket-client>=0.44.0",
    ],
    setup_requires=[
        "nose>=1.0",
    ],
    dependency_links=[
    ],
    entry_points={
        "console_scripts": [
            "russell = russell.main:cli",
            "russell-dev = russell.development.dev:cli",
            "russell-local = russell.development.local:cli",
        ],
    },
    tests_require=[
        "mock>=1.0.1",
    ],
)
