import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="serafin",
    version=read('VERSION').strip(),
    author="Mateusz 'novo' Klos",
    author_email="novopl@gmail.com",
    license="MIT",
    keywords="serafin serialize serialization json config",
    url="http://github.com/novopl/serafin",
    description="Python library that implementing selective serialization",
    long_description=read('README.rst'),
    package_dir={'serafin': 'src/serafin'},
    packages=['serafin'],
    install_requires=[
        l.strip() for l in read('ops/requirements.txt').split() if '==' in l
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
    ],
)
