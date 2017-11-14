from distutils.core import setup
from setuptools import find_packages
from pip.req import parse_requirements

requirements = parse_requirements('./requirements.txt', session=False)

setup(
  name="nhlscraper",


  description='NHL Scraper API for Python',

  packages=find_packages(),

  include_package_data=True,

  # Dependent packages (distributions)
  dependency_links=['git+https://github.com/leluso/nhlscrapi.git#egg=nhlscrapier'],
  install_requires=[str(requirement.req) for requirement in requirements],
  #install_requires=['requests', 'nhlscrapier'],
)
