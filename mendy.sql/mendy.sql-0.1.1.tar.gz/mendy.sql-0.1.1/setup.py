import codecs
import os
import sys
 
try:
    from setuptools import setup
except:
    from distutils.core import setup

 
# def read(fname):
#     return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()
 
 
 
NAME = "mendy.sql"
 
PACKAGES = ["mendy.sql",]
 
DESCRIPTION = "this is a test package for packing python liberaries tutorial."
 
LONG_DESCRIPTION = 'just have a try.'
 
KEYWORDS = "test python package"
 
AUTHOR = "Maidi"
 
AUTHOR_EMAIL = "15920164078@163.com"
 
# URL = "http://blog.useasp.net/"
 
VERSION = "0.1.1"
 
LICENSE = "MIT"
 
setup(
    name = NAME,
    version = VERSION,
    description = DESCRIPTION,
    long_description = LONG_DESCRIPTION,
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    keywords = KEYWORDS,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    # url = URL,
    license = LICENSE,
    packages = PACKAGES,
    include_package_data=True,
    zip_safe=True,
    install_requires=['pysqlite', 'SQLAlchemy']
)