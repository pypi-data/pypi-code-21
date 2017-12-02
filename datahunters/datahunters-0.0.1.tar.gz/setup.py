"""For distribution.
"""

from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
from subprocess import check_call


class PostDevelopCommand(develop):
  """Post-installation for development mode."""

  def run(self):
    check_call("apt-get install this-package".split())
    develop.run(self)


class PostInstallCommand(install):
  """Post-installation for installation mode."""

  def run(self):
    # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION
    install.run(self)


with open("./configs/requirements.txt", "r") as f:
  dep_packages = f.readlines()
  dep_packages = [x.strip() for x in dep_packages]
  print dep_packages

setup(
    name="datahunters",
    version="0.0.1",
    description="library for collecting data",
    url="https://flyfj@bitbucket.org/teamperceptance/datahunters.git",
    author="Jie Feng",
    author_email="jiefengdev@gmail.com",
    license="MIT",
    include_package_data=True,
    packages=find_packages("./"),
    install_requires=dep_packages)
