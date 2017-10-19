from distutils.core import setup
setup(
  name = 'CubeCasino',
  packages = ['CubeCasino'],
  version = '0.1',
  description = 'Building blocks for Casino games based on CubeRandom',
  author = 'Karl Zander',
  author_email = 'pvial@kryptomagik.com',
  url = 'https://github.com/pvial00/CubeCasino',
  keywords = ['games', 'entertainment', 'random'],
  classifiers = [],
  install_requires=[
      'pycube256',
      ],
)
