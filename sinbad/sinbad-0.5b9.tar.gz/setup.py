
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='sinbad',
    version='0.5b9',
    description='A library for uniform, easy access to online data sources in standard formats',
    long_description=long_description,
    url='http://cs.berry.edu/sinbad/',
    author='Nadeem Abdul Hamid',
    author_email='nadeem@acm.org',
    license='MIT',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',
    
        # Indicate who your project is intended for
        'Intended Audience :: Education',
        'Topic :: Software Development :: Libraries',
    
        # Pick your license as you wish (should match "license" above)
         'License :: OSI Approved :: MIT License',
    
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='data access xml json csv',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
           "jsonpath_rw >= 1.4.0",
           "satori-rtm-sdk >= 1.4.0",
           "xmltodict >= 0.11.0",
           "appdirs >= 1.4.3",
    ],
    python_requires='~=3.5',
    )


