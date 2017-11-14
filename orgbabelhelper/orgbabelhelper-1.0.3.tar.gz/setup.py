# we use the distribute framework that has a backward compatible invocation
# to the setuptools
from setuptools import setup

setup(
    name = "orgbabelhelper",
    version = "1.0.3",
    description = "python helper module for Emacs org mode babel",
    long_description = "python helper module for working with Emacs"
    + " org babel source blocks",
    author = "Derek Feichtinger",
    author_email = "dfeich@gmail.com",
    license = "GPL",
    url = "https://github.com/dfeich/org-babel-examples/tree/master/python",
    packages = ['orgbabelhelper'],

    install_requires = ['pandas'],
    classifiers = [
	"Development Status :: 4 - Beta",
	"Intended Audience :: Developers",
	"Programming Language :: Python :: 3"
    ]
)
