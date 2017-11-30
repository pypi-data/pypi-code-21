from distutils.core import setup
setup(
  name = 'lod',
  packages = ['lod'],
  version = '0.0.3.dev5',
  description = 'A library containing basic code useful when creating Docker Images for LegionOfDevs.com',
  long_description = 'A library containing basic code useful when creating Docker Images for LegionOfDevs.com',
  author = 'Florian Dietz',
  author_email = 'floriandietz44@gmail.com',
  url='https://legionofdevs.com',
  license = 'MIT',
  package_data={
      '': ['*.txt'], # this covers both the LICENSE.txt file in this folder, and the TRUTH.txt file in the /collab/ folder
   },
)