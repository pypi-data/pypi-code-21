from setuptools import setup, find_packages
from pip.req import parse_requirements

requirements = parse_requirements('requirements.txt', session=False)

setup(
  name="nhlscraper",
  description='NHL Scraper API for Python',
  url='https://gitlab.com/hrel3/nhlscraper',
  author='Justin Barber',
  author_email='justin@hrel.ca',
  python_requires='>=3.6',
  packages=find_packages(),
  version='0.1.2',
  include_package_data=True,
  # Dependent packages (distributions)
  dependency_links=['git+https://github.com/leluso/nhlscrapi.git#egg=nhlscrapier'],
  install_requires=[str(requirement.req) for requirement in requirements],
)
