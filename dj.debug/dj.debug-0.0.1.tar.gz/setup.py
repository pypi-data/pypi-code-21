"""
dj.debug
"""

import os

from setuptools import setup, find_packages


version = "0.0.1"


install_requires = ['django']
extras_require = {}
extras_require['test'] = [
    "pytest",
    "pytest-mock",
    "pytest-django",
    "pytest-capturelog",
    "pytest-coverage",
    "coverage",
    "codecov",
    "flake8"]


def read(*rnames):
    return open(
        os.path.join(
            os.path.dirname(__file__), *rnames)).read()


long_description = (
    'Detailed documentation\n'
    + '**********************\n'
    + '\n'
    + read("README.rst")
    + '\n')

try:
    long_description += (
        '\n'
        + read("dj", "debug", "README.rst")
        + '\n')
except IOError:
    pass

setup(
    name='dj.debug',
    version=version,
    description="Debugging tools for django",
    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules"],
    keywords='',
    author='Ryan Northey',
    author_email='ryan@synca.io',
    url='http://github.com/phlax/dj.debug',
    license='GPL3',
    packages=find_packages(),
    namespace_packages=['dj'],
    package_data={'': ['*.rst']},
    include_package_data=True,
    zip_safe=False,
    test_suite="dj.debug.tests",
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points="""
    # -*- Entry points: -*-
    """)
