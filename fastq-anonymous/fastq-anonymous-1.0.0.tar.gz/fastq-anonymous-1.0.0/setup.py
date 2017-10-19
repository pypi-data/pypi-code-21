# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
exec(open('fastqanonymous/version.py').read())

setup(
    name='fastq-anonymous',
    version=__version__,
    description='Change the sequence of a fastq file to enable sharing of confidential information, for troubleshooting￼ of tools.',
    long_description=open(path.join(here, "README.rst")).read(),
    url='https://github.com/wdecoster/fastq-anonymous',
    author='Wouter De Coster',
    author_email='decosterwouter@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='nanopore sequencing plotting quality control',
    packages=find_packages(),
    install_requires=['biopython'],
    package_data={'fastq-anonymous': []},
    package_dir={'fastq-anonymous': 'fastq-anonymous'},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'fastq-anonymous=fastqanonymous.fastqanonymous:main',
        ],
    },
)
