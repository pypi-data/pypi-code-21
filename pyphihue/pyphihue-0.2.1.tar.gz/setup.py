#from distutils.core import setup
from setuptools import setup
from pyphihue import __author__
from pyphihue import __version__


VER = "{}.{}.{}".format(*__version__)
URL = 'https://gitlab.com/pyphihue/pyphihue'

setup(name='pyphihue',
      packages=['pyphihue'],
      version=VER,
      description='A library to interface with Philips Hue',
      author=__author__,
      author_email='pydevpat@gmail.com',
      url=URL,
      download_url='{}/repository/archive.tar.gz?ref=master'.format(URL),
      license='MIT',
      keywords='Philips Hue API-wrapper',
      install_requires=['requests'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Home Automation',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6'
    ],
)
