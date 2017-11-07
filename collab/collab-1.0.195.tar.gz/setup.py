from distutils.core import setup
setup(
  name = 'collab',
  packages = ['collab'],
  version = '1.0.195',
  description = 'A library containing basic code useful when creating Docker Images for Collab',
  long_description = 'A library containing basic code useful when creating Docker Images for Collab',
  author = 'Florian Dietz',
  author_email = 'floriandietz44@gmail.com',
  url='http://example.com',
  license = 'MIT',
  package_data={
      '': ['*.txt'], # this covers both the LICENSE.txt file in this folder, and the TRUTH.txt file in the /collab/ folder
   },
)