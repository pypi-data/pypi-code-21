from distutils.core import setup
setup(
  name = 'battle_tested',
  packages = ['battle_tested'], # this must be the same as the name above
  version = '2017.10.19',
  install_requires = ["hypothesis", "stricttuple", "prettytable", "generators"],
  description = 'automated function fuzzer based on hypothesis to easily test production code',
  author = 'Cody Kochmann',
  author_email = 'kochmanncody@gmail.com',
  url = 'https://github.com/CodyKochmann/battle_tested',
  download_url = 'https://github.com/CodyKochmann/battle_tested/tarball/2017.10.19',
  keywords = ['battle_tested', 'test', 'hypothesis', 'fuzzing', 'fuzz', 'production', 'unittest'],
  classifiers = [],
)
