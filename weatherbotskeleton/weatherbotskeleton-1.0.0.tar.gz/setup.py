from os import path
from setuptools import setup, find_packages

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, "VERSION"), encoding="utf-8") as f:
    VERSION = f.read().strip()

setup(author="Andrew Michaud",
      author_email="bots+weatherbotskeleton@mail.andrewmichaud.com",
      install_requires=["botskeleton>=1.2.2", "requests>=2.11.1"],
      python_requires=">=3.6",
      license="BSD3",
      name="weatherbotskeleton",
      packages=find_packages(),
      url="https://github.com/andrewmichaud/weatherbotskeleton",
      version=VERSION)
