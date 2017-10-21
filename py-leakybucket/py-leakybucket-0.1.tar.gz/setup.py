# -*- coding: utf-8 -*-
import os
from distutils.core import setup

__author__ = 'christian'
__created__ = '01.09.2017'


def read(fname):
    """
    Utility function to read the README file.
    Used for the long_description.  It's nice, because now 1) we have a top level
    README file and 2) it's easier to type in the README file than to put a raw
    string in below ...

    :param fname: file name
    :return: file content
    :rtype: str
    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="py-leakybucket",
    version="0.1",
    author="Christian Scholz",
    author_email="c.scholz@c-s-media.net",
    description=("Python Leaky Bucket Rate Limiter with hourly limiting i.e. required for "
                 "Amazon Marketplace Webservices"),
    long_description=read('README.txt'),
    license="GNU GENERAL PUBLIC LICENSE",
    keywords=["leakybucket", "ratelimiter"],
    url="https://github.com/Sprungwunder/py-leakybucket",
    download_url="https://github.com/Sprungwunder/py-leakybucket/archive/0.1.tar.gz",
    packages=['ratelimit', 'tests'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Topic :: Utilities",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers"
    ],
    install_requires=[
        'redis',
    ],
    tests_require=[
        'fakeredis'
    ]
)
