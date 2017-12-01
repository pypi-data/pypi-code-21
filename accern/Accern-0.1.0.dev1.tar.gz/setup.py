"""
Official Accern Bindings for Python.

===================================
A Python library for Accern's API.


Setup
-----

You can install this package by using the pip tool and installing:

    $ pip install accern

Setting up a Accern Account
---------------------------

Sign up for Accern at https://feed.accern.com.

Using the Accern API
--------------------

Documentation for Accern API can be found here:

- https://doc.accern.com

To view the full content of Accern API, you would need to provide your
Accern API Token.

"""
import sys


from accern.version import VERSION

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.version_info <= (2, 6):
    error = 'Requires Python Version 2.5 or above... exiting.'
    print (sys.stderr, error)
    sys.exit(1)


requirements = [
    'requests>=2.11.1,<3.0'
]

setup(
    name='Accern',
    version=VERSION,
    description="A python library for Accern Data API",
    long_description=__doc__,
    license='MIT License',
    url="https://github.com/Accern/accern-python",
    packages=['accern'],
    platforms='Posix; MacOS X; Windows',
    setup_requires=requirements,
    install_requires=requirements,
    classifiers=['Development Status :: 1 - Planning',
                 'Intended Audience :: Developers',
                 'Intended Audience :: Financial and Insurance Industry',
                 'Topic :: Office/Business :: Financial :: Investment',
                 'License :: OSI Approved :: MIT License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.6',
                 'Programming Language :: Python :: 2.7'
                 ]
)
