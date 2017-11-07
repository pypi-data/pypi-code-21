from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='agensgraph',
    version='0.0.1',
    description='A Python driver for Agensgraph',
    long_description=long_description,
    url='https://github.com/iomedhealth/agensgraph',
    author='IOMED Medical Solutions SL',
    author_email='dev@iomed.es',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='postgres, agensgraph, psycopg2',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['psycopg2'],
    extras_require={
        'test': ['coverage', 'pytest'],
    }
)
