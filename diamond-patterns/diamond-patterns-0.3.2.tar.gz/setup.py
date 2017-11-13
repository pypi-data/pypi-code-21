import os
import re
import codecs
from setuptools import setup
from setuptools import find_packages


def read(*rnames):
    return codecs.open(os.path.join(os.path.dirname(__file__), *rnames), 'r', 'utf-8').read()


def grep(attrname):
    pattern = r"{0}\W*=\W*'([^']+)'".format(attrname)
    strval, = re.findall(pattern, read('diamond_patterns/__meta__.py'))
    return strval


setup(
    version=grep('__version__'),
    name='diamond-patterns',
    description="Diamond-Patterns are scaffolds for knowledge work.  Use patterns to go faster.",
    scripts=[
        "bin/diamond",
        "bin/diamond.cmd",
    ],
    long_description=read('Readme.rst'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        "Operating System :: POSIX :: BSD",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Topic :: Office/Business",
    ],
    packages=find_packages(),
    include_package_data=True,
    keywords='',
    author=grep('__author__'),
    author_email=grep('__email__'),
    url=grep('__url__'),
    install_requires=read('requirements.txt'),
    license='MIT',
    zip_safe=False,
)
