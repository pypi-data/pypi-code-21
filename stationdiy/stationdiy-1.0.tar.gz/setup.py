from distutils.core import setup
setup(
  name = 'stationdiy',
  packages = ['stationdiy'], # this must be the same as the name above
  version = '1.0',
  description = 'Custom Controller for StationDiY IoT platform',
  author = 'Baurin Leza',
  author_email = 'baurin.lg@gmail.com',
  url = 'https://github.com/trpill/stationdiy', # use the URL to the github repo
  download_url = 'https://github.com/trpill/stationdiy/archive/master.zip', # I'll explain this in a second
  keywords = ['stationdiy', 'iot', 'internet'], #  keywords
  classifiers = [],
  install_requires=[
        'paho-mqtt',
        'requests',
    ]
)
