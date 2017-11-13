from distutils.core import setup
setup(
  name = 'lod-executor',
  packages = ['collab'],
  version = '0.0.2',
  description = 'A program for interacting with the Server of LegionOfDevs.com',
  long_description = 'A program for interacting with the API of LegionOfDevs.com',
  author = 'Florian Dietz',
  author_email = 'floriandietz44@gmail.com',
  url='http://example.com',
  license = 'MIT',
  package_data={
      '': ['*.txt', # this covers both the LICENSE.txt file in this folder, and the TRUTH.txt file in the /collab/ folder
        ],
   },
   entry_points = {
        'console_scripts': [
            'lod-executor=collab.lod_executor:main',
        ],
    },
    install_requires=[
        'bottle',
        'docker',
        'python-dateutil',
    ],
)