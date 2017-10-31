#!/usr/bin/env python
from setuptools import setup, find_packages
import graphiti


with open("README.rst", "r") as resource:
    LONG_DESCRIPTION = resource.read()

setup(
    name="graphiti",
    version=graphiti.__version__,
    author="ASD Technologies",
    author_email="admin@asdco.ru",
    description="Graphite/Carbon client",
    long_description=LONG_DESCRIPTION,
    license="MIT",
    url="https://bitbucket.org/asdtech/graphiti",
    packages=find_packages("."),
    test_suite="graphiti.tests",
    setup_requires="six",
    install_requires=["six"],
    extras_require={"cmd": ["docopt"]},
    entry_points={'console_scripts': ['graphiti = graphiti.cmd:main']},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 3.4",
        "Topic :: Internet",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking",
        "Topic :: System :: Networking :: Monitoring"
    ],
    zip_safe=True
)
