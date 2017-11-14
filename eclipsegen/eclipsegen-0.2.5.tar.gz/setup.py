import os
import shutil
import tempfile
import urllib
from zipfile import ZipFile

from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install

_DIRECTOR_URL = 'http://eclipse.mirror.triple-it.nl/tools/buckminster/products/org.eclipse.equinox.p2.director.product_1.7.0.v20150718-2211.zip'
_DIRECTOR_DIR = os.path.join(os.path.dirname(__file__), 'eclipsegen', 'director')
_DIRECTOR_UNPACK_DIR = os.path.join(os.path.dirname(__file__), 'eclipsegen')


def _download_director():
  if os.path.isdir(_DIRECTOR_DIR):
    shutil.rmtree(_DIRECTOR_DIR, ignore_errors=True)
  with tempfile.TemporaryFile(prefix='p2-director', suffix='.zip') as tmpfile:
    with urllib.request.urlopen(_DIRECTOR_URL) as response:
      shutil.copyfileobj(response, tmpfile)
    with ZipFile(tmpfile) as zipFile:
      zipFile.extractall(path=_DIRECTOR_UNPACK_DIR)
  # Make director executable
  os.chmod(os.path.join(_DIRECTOR_DIR, 'director'), 0o744)
  os.chmod(os.path.join(_DIRECTOR_DIR, 'director.bat'), 0o744)
  # Delete unused Python file in Ant plugin which should not be compiled
  runantFile = os.path.join(_DIRECTOR_DIR, 'plugins', 'org.apache.ant_1.9.4.v201504302020', 'bin', 'runant.py')
  os.remove(runantFile)


class PostDevelopCommand(develop):
  def run(self):
    _download_director()
    develop.run(self)


class PostInstallCommand(install):
  def run(self):
    _download_director()
    install.run(self)


dependencies = [
  'requests==2.10.0'
]

setup(
  name='eclipsegen',
  version='0.2.5',
  description='Generate Eclipse instances in Python',
  url='http://github.com/Gohla/eclipsegen',
  author='Gabriel Konat',
  author_email='gabrielkonat@gmail.com',
  license='Apache 2.0',
  packages=['eclipsegen'],
  install_requires=dependencies,
  test_suite='nose.collector',
  tests_require=['nose>=1.3.7'] + dependencies,
  include_package_data=True,
  zip_safe=False,
  cmdclass={
    'install': PostInstallCommand,
    'develop': PostDevelopCommand
  }
)
