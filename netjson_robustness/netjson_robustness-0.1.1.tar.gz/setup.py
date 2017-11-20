from distutils.core import setup
setup(
  name='netjson_robustness',
  packages=['netjson_robustness'],
  version='0.1.1',
  description='A library to perform some robustness analysis on '
          'NetJSON-defined graphs',
  author='Leonardo Maccari',
  author_email='maccari@disi.unitn.it',
  url='https://github.com/netCommonsEU/netjson_robustness',
  download_url='https://github.com/netCommonsEU/netjson_robustness/'
               'archive/0.1.tar.gz',
  keywords=['NetJSON', 'graph analysis', 'robustness'],
  install_requirements='networkx',
  classifiers=[],
)
