import sys
from setuptools import setup, find_packages

if sys.version_info.major < 3:
    sys.exit("Error: Please upgrade to Python3")


def get_long_description():
    with open("README.rst") as fp:
        return fp.read()


setup(name="yatodol",
      version="0.0.1",
      description="Yet another todo-list manager (command line interface)",
      long_description=get_long_description(),
      url="https://github.com/yatodol/cli",
      author="Dimitri Merejkowsky",
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
        "python-cli-ui",
      ],
      classifiers=[
        "Programming Language :: Python :: 3.6",
      ],
      entry_points={
        "console_scripts": [
          "yatodol = yatodol:main",
         ]
      }
      )
