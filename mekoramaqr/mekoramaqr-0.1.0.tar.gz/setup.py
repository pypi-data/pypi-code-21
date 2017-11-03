"""setuptools based setup script.

This uses setuptools which is now the standard python mechanism for
installing packages. If you have downloaded and uncompressed the
source code, or fetched it from git, for the simplest
installation just type the command::

    python setup.py install

However, you would normally install the latest release from
the PyPI archive with::

    pip install mekoramaqr

"""
from __future__ import print_function

import sys
import logging

try:
    from setuptools import setup, find_packages
    import setuptools.command.test
    from setuptools.command.develop import develop
    from setuptools.command.install import install

except ImportError:
    sys.exit("We need the Python library setuptools to be installed. Try runnning: python -m ensurepip")


class TestCommand(setuptools.command.test.test, object):
    """ Setuptools test command explicitly using test discovery. """

    def _test_args(self):
        yield 'discover'
        for arg in super(TestCommand, self)._test_args():
            yield arg


# zbar can cause segfaults on MacOS. Try to test for this
def test_zbar():
    if sys.platform == "darwin":
        logging.warn("Testing for a working zbar installation. This is known to crash with a segfault on MacOS with default zbar 0.10.\n"
                     "\n"
                     "If this crashes, install the fixed version like this:\n"
                     "\n"
                     "    pip install --upgrade git+https://github.com/npinchot/zbar.git\n"
                     "\n")
    try:
        import zbar
        return True
    except Exception as e:
        logging.error("Invalid zbar installation. Check that `python -c 'import zbar'` works successfully.")
        logging.exception(e)
        return False


class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        test_zbar()
        develop.run(self)

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        test_zbar()
        install.run(self)


# Using requirements.txt is preferred for an application
# (and likely will pin specific version numbers), using
# setup.py's install_requires is preferred for a library
# (and should try not to be overly narrow with versions).


# Define the version number in __init__.py
__version__ = "Undefined"
for line in open('mekoramaqr/__init__.py'):
    if line.startswith('__version__'):
        exec(line.strip())

setup(name='mekoramaqr',
      version=__version__,
      author='MekoramaQR Contributors',
      author_email='gepeto.mekorama@gmail.com',
      url='https://bitbucket.org/gepeto213/mekoramaqr',
      description='Tools for reading, writing, and editing Mekorama level QR Codes',
      # long_description=readme_rst,
      download_url='https://bitbucket.org/gepeto213/mekoramaqr/downloads/',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: End Users/Desktop',
          'License :: Freely Distributable',
          'License :: OSI Approved',
          'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          #'Programming Language :: Python :: 3',
          #'Programming Language :: Python :: 3.4',
          #'Programming Language :: Python :: 3.5',
          #'Programming Language :: Python :: 3.6',
          'Topic :: Games/Entertainment',
          'Topic :: Games/Entertainment :: Puzzle Games',
      ],
      keywords=['games', 'mekorama', 'qr code', 'cli'],
      install_requires=[
          'numpy',
          'Pillow',
          'qrcode >= 5',
          'qrtools',
          'six',
          'zbar >= 0.10',
      ],
      cmdclass={
          'test': TestCommand,
          'develop': PostDevelopCommand,
          'install': PostInstallCommand,
      },
      packages=find_packages(),
      entry_points={
          'console_scripts':["mekoramaqr=mekoramaqr.__main__:main"],
          },
      )
