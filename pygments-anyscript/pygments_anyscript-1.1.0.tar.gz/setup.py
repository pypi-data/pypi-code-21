#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
import os
import io
import re

from setuptools import find_packages, setup


def find_version(file_path, **kwargs):
    """Parse the __version__ string from a file."""
    with io.open(
        os.path.join(os.path.dirname(__file__), file_path),
        encoding=kwargs.get("encoding", "utf8")
    ) as fp:
        version_file = fp.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if not version_match:
        raise RuntimeError("Unable to find version string.")
    return version_match.group(1)


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'pygments',
]

setup_requirements = []

test_requirements = [
    'pytest',
    'pygments'
]

setup(
    name='pygments_anyscript',
    version=find_version("pygments_anyscript/__init__.py"),
    description="Pygments lexer and style for the AnyScript language",
    long_description=readme + '\n\n' + history,
    author="Morten Enemark Lund",
    author_email='mel@anybodytech.com',
    url='https://github.com/AnyBody/pygments-anyscript',
    packages=find_packages(include=['pygments_anyscript']),
    entry_points={
        'pygments.lexers':
            ['AnyScript = pygments_anyscript:AnyScriptLexer',
             'AnyScriptDoc = pygments_anyscript:AnyScriptDocLexer'],
        'pygments.styles':
            ['AnyScript = pygments_anyscript:AnyScriptStyle']
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords=["pygments", "pygments_anyscript", "lexer",
              "anyscript", "AnyBody Modeling System"],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
