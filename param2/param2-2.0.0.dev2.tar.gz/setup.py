import sys

import versioneer

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


install_requires = []
if sys.version_info[0]==2 and sys.version_info[1]<7:
    install_requires+=['ordereddict','unittest2']


setup_args = dict(
    name='param2',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='Work in progress; use at own risk (also: declarative Python programming using Parameters).',
    long_description=open('README.rst').read(),
    license='BSD',
    url='http://gitlab.com/ceball/param2/',
    packages = ["param"],
    provides = ["param"],
    install_requires = install_requires,
    classifiers = [
        "License :: OSI Approved :: BSD License",
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries"]
)

if __name__=="__main__":
    setup(**setup_args)
