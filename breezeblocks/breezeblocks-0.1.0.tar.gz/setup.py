from setuptools import setup
from setuptools import find_packages

with open('README.rst', 'r') as f:
    long_description=f.read()

setup(name='breezeblocks',
    version='0.1.0',
    description='A lightweight SQL Querying package.',
    author='Quinn Mortimer',
    author_email='quinn.e.mortimer@gmail.com',
    url='https://github.com/modimore/BreezeBlocks',
    license='MIT',
    packages=find_packages('package'),
    package_dir={ '': 'package' },
    long_description=long_description,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Database :: Front-Ends",
        "Operating System :: OS Independent"
    ],
)
