import time

from setuptools import find_packages

from distutils.core import setup

patch_level = int(time.time())

ver = "0.1." + str(patch_level)[1:]

setup(
  name = 'smashbot',
  packages = find_packages(),
  version = ver,
  description = 'Python Code for Slackbot Tech Training Demo',
  author = 'Wray Mills',
  author_email = 'wray@wrayesian.com',
  url = 'https://github.com/wray/slack_smashbot',
  download_url = 'https://github.com/wray/slack_smashbot/tarball/'+ver,
  keywords = ['slackbot', 'RPi', 'AWS'],
  classifiers = [],
)
