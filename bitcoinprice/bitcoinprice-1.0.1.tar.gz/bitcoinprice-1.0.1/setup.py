""" Bitcoinprice.
See:
https://github.com/danjellesma/bitcoinprice
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

setup(
    name='bitcoinprice',
    version='1.0.1',
    description='Retrieves the current Bitcoin Price',
    url='https://github.com/danjellesma/bitcoinprice',
    author='Dan Jellesma',
    author_email='danjellesma@googlegroups.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='bitcoin bitcoinapi',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['requests'],
)
