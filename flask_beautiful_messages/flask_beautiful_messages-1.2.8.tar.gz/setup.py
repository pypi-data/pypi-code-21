from setuptools import setup

setup(
  name = 'flask_beautiful_messages',
  packages = ['flask_beautiful_messages'],
  package_dir={'flask_beautiful_messages': 'flask_beautiful_messages'},
  package_data={'flask_beautiful_messages': ['flask_beautiful_messages/*']},
  exclude_package_data = {'flask_beautiful_messages': ['__pycache__',]},
  include_package_data=True,
  version = '1.2.8',
  description = 'This library allows Flask developers to quickly create beautiful email and webpage templates',
  author = 'Herbert Dawkins',
  author_email = 'DrDawkins@ClearScienceInc.com',
  url = 'https://github.com/sudouser2010/flask_beautiful_messages',
  download_url = 'https://github.com/sudouser2010/flask_beautiful_messages/archive/1.2.8.tar.gz',
  keywords = ['flask', 'beautiful', 'messages', 'email', 'webpage', 'template'],
  classifiers = [],
  install_requires=['flask==0.12.2'],
)
