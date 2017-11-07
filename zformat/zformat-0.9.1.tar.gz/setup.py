"""Setuptools based install.


For more on this file:
    https://packaging.python.org/en/latest/distributing.html

Version:
    Use a PEP440 and Semantic version number (http://semver.org/)!
    For discussion on how to single-source the version number, see:
        https://packaging.python.org/en/latest/single_source_version.html
"""


from setuptools import setup, find_packages
from codecs import open
from os import path

readme = open(path.join(path.abspath(path.dirname(__file__)), 'README.md'), encoding='utf-8').read()

setup(
    name='zformat',
    version='v0.9.1',
    setup_requires=['setuptools_scm'],
    description='An opinionated CLI format checker, formatter and minimizer for JavaScript and CSS.',
    long_description=readme,
    author='Josh Ziegler',
    author_email='josh.s.ziegler@gmail.com',
    license='MIT',
    url='https://github.com/joshsziegler/z-format',
    py_modules=[
        'cssformatter',
        'format',
    ],
    python_requires='>=3.4',
    install_requires=[
        'jsbeautifier >= 1.6',
        'jsmin >= 2.2',
    ],
    entry_points={ # Cross-platform (CLI) entry points for pip to create
        'console_scripts': [
            'zformat=zformat:main',
        ],
    },
)
