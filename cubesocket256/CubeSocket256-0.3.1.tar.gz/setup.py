from distutils.core import setup
setup(
  name = 'CubeSocket256',
  packages = ['CubeSocket256'],
  version = '0.3.1',
  description = 'Socket bindings using the Cube256 cipher for encryption and decryption (Uses DHE)',
  author = 'Karl Zander',
  author_email = 'pvial@kryptomagik.com',
  url = 'https://github.com/pvial00/CubeSocket256',
  keywords = ['cryptography', 'encryption', 'security', 'network'],
  classifiers = [],
  install_requires=[
      'pycrypto'
      ],
)
