from distutils.core import setup
from setuptools import find_packages
setup(
  name = 'lodtools',
  packages = ['collab',],
  version = '1.0.75',
  description = 'A program for interacting with the API of LegionOfDevs.com',
  long_description = 'A program for interacting with the API of LegionOfDevs.com',
  author = 'Florian Dietz',
  author_email = 'floriandietz44@gmail.com',
  url='https://legionofdevs.com',
  license = 'MIT',
  package_data={
      '': ['*.txt', # this covers both the LICENSE.txt file in this folder, and the TRUTH.txt file in the /collab/ folder
          'fibonacci/*', # this covers the data in the Docker program example folder
          'input_examples/*'], # this covers the data in the input example folder
   },
   entry_points = {
        'console_scripts': [
            'lod-tools=collab.lod_tools:main',
        ],
    },
    install_requires=[
        'docker',
    ],
)