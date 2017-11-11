
from setuptools import setup, find_packages

# README file as long_description:
long_description = open('README.rst').read()

# Read in requirements.txt
requirements = open('requirements.txt').readlines()
requirements = [r.strip() for r in requirements]

setup(
    name='chemkin_grp11',
    version='0.1.1',
    description='Simple chemical kinetics code',
    long_description=long_description,
    install_requires=requirements,
    url='https://github.com/cs207-group11/chemkin_grp11',
    author='hs',
    author_email='hsim13372@gmail.com',
    license='MIT',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    zip_safe=False
    )
