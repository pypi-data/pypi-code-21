from distutils.core import setup

#note to self: see http://peterdowns.com/posts/first-time-with-pypi.html for setup

setup(
  name = 'easingutilities',
  packages = ['easingutilities'], # this must be the same as the name above
  version = '0.1',
  description = 'A controller for controlling Dynamixel motors with easing algorithms through pypot',
  author = 'Graunephar',
  author_email = 'daniel@graungaard.com',
  url = 'https://github.com/Robot-Boys/Easing-utilities', # use the URL to the github repo
  download_url = 'https://github.com/Robot-Boys/Easing-utilities/archive/0.1.tar.gz', # Link created via github tag
  keywords = ['Dynamixel', 'Eading', 'Motor'],
  classifiers = [],
)