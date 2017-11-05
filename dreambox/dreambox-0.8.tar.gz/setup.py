from distutils.core import setup
setup(
  name = 'dreambox',
  packages = ['dreambox'], 
  version = '0.8',
  description = 'Dreambox lib, tested with dm-800HD se',
  author = 'Damiano Pertolunio',
  author_email = 'spamtrap@gmail.com',
  url = 'https://github.com/eneasz/dreambox', 
  download_url = 'https://github.com/eneasz//dreambox/archive/0.8.tar.gz',
  keywords = ['Dreambox', 'DM800 HD', 'DM800 HD se', 'Dream', 'Multimedia'], 
  classifiers = [],
  long_description = open('README.md').read(),
  install_requires=['lxml']
)
