from distutils.core import setup
setup(
  name = 'Krypto4Nazis',
  packages = ['Krypto4Nazis'],
  version = '0.1.2',
  description = 'Tools for securely transmitting A-Z messages',
  author = 'Karl Zander',
  author_email = 'pvial@kryptomagik.com',
  url = 'https://github.com/pvial00/MorseStation',
  keywords = ['cryptography', 'encryption', 'security'],
  classifiers = [],
  install_requires=[
      'pycube',
      'MorseStation',
      'KlassiKrypto',
      ],
)
