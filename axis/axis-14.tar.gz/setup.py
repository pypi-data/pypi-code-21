# https://jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/
# http://peterdowns.com/posts/first-time-with-pypi.html
# Upload to PyPI Live
# python setup.py sdist upload -r pypi

from setuptools import setup

setup(
  name='axis',
  packages=['axis'],
  version='14',
  description='A python library for communicating with devices from Axis Communications',
  author='Robert Svensson',
  author_email='Kane610@users.noreply.github.com',
  license='MIT',
  url='https://github.com/Kane610/axis',
  download_url='https://github.com/Kane610/axis/archive/v14.tar.gz',
  install_requires=['requests'],
  keywords=['axis', 'vapix', 'onvif', 'event stream', 'homeassistant'],
  classifiers=[],
)
