# -*- coding: utf-8 -*-
import inspect
import sys
from codecs import open
from os.path import join, abspath, realpath, dirname

from setuptools import setup, find_packages


# Sadly we cannot use the location here because of the typing module which isn't in Python < 3.5
def script_dir(pyobject, follow_symlinks=True):
    """Get current script's directory

    Args:
        pyobject (Any): Any Python object in the script
        follow_symlinks (Optional[bool]): Follow symlinks or not. Defaults to True.

    Returns:
        str: Current script's directory
    """
    if getattr(sys, 'frozen', False):  # py2exe, PyInstaller, cx_Freeze
        path = abspath(sys.executable)
    else:
        path = inspect.getabsfile(pyobject)
    if follow_symlinks:
        path = realpath(path)
    return dirname(path)


def script_dir_plus_file(filename, pyobject, follow_symlinks=True):
    """Get current script's directory and then append a filename

    Args:
        filename (str): Filename to append to directory path
        pyobject (Any): Any Python object in the script
        follow_symlinks (Optional[bool]): Follow symlinks or not. Defaults to True.

    Returns:
        str: Current script's directory and with filename appended
    """
    return join(script_dir(pyobject, follow_symlinks), filename)


def get_version():
    version_file = open(script_dir_plus_file('version.txt', get_version), encoding='utf-8')
    return version_file.read()


def get_readme():
    readme_file = open(script_dir_plus_file('README.rst', get_readme), encoding='utf-8')
    return readme_file.read()


setup(name='ummalqura',
      version=get_version(),
      description='Python Hijri Umalqurra',
      url='https://github.com/borni-dhifi/ummalqura',
      author='Borni DHIFI',
      author_email='dhifi.borni@gmail.com',
      keywords=['ummalqura'],
      long_description=get_readme(),
      license='Waqef',
      packages=['ummalqura'],
      zip_safe=False)
