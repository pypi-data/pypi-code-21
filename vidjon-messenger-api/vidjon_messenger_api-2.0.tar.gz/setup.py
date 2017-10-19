from setuptools import setup, find_packages


setup(
  name = 'vidjon_messenger_api',
  packages = find_packages(),
  version = '2.0',
  description = 'A simple API for sending and receiving messages with a registered user.',
  author = 'Vidar Jonsson',
  author_email = 'vidjon@gmail.com',
  url = 'https://github.com/vidjon/messenger_v2', # use the URL to the github repo
  keywords = ['messenger_api', 'vidjon'],
  install_requires=[
    'flask',
    'flask_jwt',
    'flask_restplus',
    'flask_sqlalchemy',

  ],
  classifiers=[
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3',
    'Topic :: Software Development :: Libraries :: Python Modules'],
    entry_points={
    'console_scripts': [
      'vidjon_messenger_api = vidjon_messenger_api.app:main'
    ],
  },
)