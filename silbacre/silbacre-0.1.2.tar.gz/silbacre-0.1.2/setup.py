import os

from setuptools import setup
config_path = os.path.join(os.path.expanduser("~"), ".loquitor")
py_modules = ['bot', 'skeleton']
setup(name='silbacre',
      version='0.1.2',
      description='Silence (SMSSecure) backup file API',
      author='Ralph Embree',
      author_email='ralph.embree@brominator.org',
      url='https://gitlab.com/ralphembree/silbacre',
      #packages=['silbacre'],
      install_requires=['bs4', 'phonenumbers', 'strudel'],
      scripts=['silbacre'],
)
