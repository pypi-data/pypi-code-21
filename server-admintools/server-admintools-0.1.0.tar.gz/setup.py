"""
Copyright 2017 Hermann Krumrey

This file is part of server-admintools.

server-admintools is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

server-admintools is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with server-admintools.  If not, see <http://www.gnu.org/licenses/>.
"""

# imports
import os
import sys
from server_admintools import version
from server_admintools.sudo import quit_if_not_sudo
from setuptools import setup, find_packages


def readme():
    """
    Reads the readme file and converts it to RST if pypandoc is
    installed. If not, the raw markdown text is returned
    :return: the readme file as a string
    """
    # noinspection PyBroadException
    try:
        # noinspection PyPackageRequirements,PyUnresolvedReferences
        import pypandoc
        with open("README.md") as f:
            # Convert markdown file to rst
            markdown = f.read()
            rst = pypandoc.convert(markdown, "rst", format="md")
            return rst

    except ModuleNotFoundError:
        # If pandoc is not installed, just return the raw markdown text
        with open("README.md") as f:
            return f.read()


def find_scripts():
    """
    Returns a list of scripts in the bin directory
    :return: the list of scripts
    """
    scripts = []

    for file_name in os.listdir("bin"):

        path = os.path.join("bin", file_name)
        if file_name == "__init__.py":
            continue
        elif not os.path.isfile(path):
            continue
        else:
            scripts.append(os.path.join("bin", file_name))

    return scripts


if "install" in sys.argv:
    quit_if_not_sudo()
setup(
    name="server-admintools",
    version=version,
    description="A collection of server administration bin",
    long_description=readme(),
    classifiers=[
        "Environment :: Console",
        "Natural Language :: English",
        "Intended Audience :: System Administrators",
        "Development Status :: 1 - Planning",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
    ],
    url="https://gitlab.namibsun.net/namboy94/server-admintools",
    download_url="https://gitlab.namibsun.net/namboy94/"
                 "server-admintools/repository/archive.zip?ref=master",
    author="Hermann Krumrey",
    author_email="hermann@krumreyh.com",
    license="GNU GPL3",
    packages=find_packages(),
    install_requires=[],
    test_suite='nose.collector',
    tests_require=['nose'],
    scripts=find_scripts(),
    zip_safe=False
)
