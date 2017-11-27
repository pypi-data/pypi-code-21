from distutils.core import setup
from setuptools import find_packages

VERSION = '0.1.0b1'

setup(
    name='graphene-extensions',
    version=VERSION,
    description='GraphQL framework for django',
    long_description=open('README.rst').read(),

    author='Karol Gruszczyk',
    author_email='karol.gruszczyk@gmail.com',

    packages=[package for package in find_packages() if 'tests' not in package],

    url='https://github.com/karol-gruszczyk/graphene-extenstions/',
    keywords='graphql framework django relay graphene',

    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='~=3.6',

    install_requires=[
        'graphene>=2.0<3',
        'django>=1.10<2',
    ],
)
