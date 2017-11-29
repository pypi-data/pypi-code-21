from distutils.core import setup
setup(
  name = 'MorseStation',
  packages = ['MorseStation'],
  version = '0.1.2',
  description = 'Tool for converting A-Z messages into Morse code Wave files',
  author = 'Karl Zander',
  author_email = 'pvial@kryptomagik.com',
  url = 'https://github.com/pvial00/MorseStation',
  keywords = ['cryptography', 'encryption', 'security'],
  classifiers = [],
  install_requires=[
      'KlassiKrypto',
      ],
)
