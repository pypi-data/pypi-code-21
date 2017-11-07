
from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.txt"), encoding="utf-8") as f:
  long_description = f.read()

setup(
  name = "bomail",
  version = "0.9.0.1",
  description = "A homemade, hobbyist, hacky system for organizing and interacting with email.",
  long_description = long_description,
  url = "https://bitbucket.org/bowaggonerpublic/bomail",
  author = "Bo Waggoner",
  author_email = "luv2runxc@gmail.com",
  install_requires = ["datetime", "python-dateutil"],
  python_requires = ">=3.3",
  packages = find_packages(exclude=['contrib', 'docs', 'tests']), #["bomail"],
  entry_points = {
    "console_scripts": ["bomail = bomail.bomail:main"]
  }
  )  # end setup

