# -*- coding: utf-8 -*-
# pylint: disable=broad-except
"""qatestlink module can be installed and configured from here"""

from os import path
from setuptools import setup, find_packages
from qatestlink.core.utils.Utils import read_file
from qatestlink.core.utils.Utils import path_format


CURR_PATH = "{}{}".format(path.abspath(path.dirname(__file__)), '/')


def read(file_name=None, is_encoding=True, ignore_raises=False):
    """Read file"""
    if file_name is None:
        raise Exception("File name not provided")
    if ignore_raises:
        try:
            return read_file(is_encoding=is_encoding,
                             file_path=path_format(
                                 file_path=CURR_PATH,
                                 file_name=file_name,
                                 ignore_raises=ignore_raises))
        except Exception:
            #TODO: not silence like this,
            # must be on setup.cfg, README path
            return 'NOTFOUND'
    return read_file(is_encoding=is_encoding,
                     file_path=path_format(
                         file_path=CURR_PATH,
                         file_name=file_name,
                         ignore_raises=ignore_raises))


setup(
    name='qatestlink',
    version='0.0.1',
    license=read("LICENSE", is_encoding=False, ignore_raises=True),
    packages=find_packages(exclude=['tests']),
    description='Main automation lib',
    long_description=read("README.rst"),
    author='Netzulo Open Source',
    author_email='netzuleando@gmail.com',
    url='https://github.com/netzulo/qatestlink',
    download_url='https://github.com/netzulo/qatestlink/tarball/v0.0.1',
    keywords=[
        'testing',
        'logging',
        'functional',
        'http',
        'test',
        'testlink',
        'XMLRPC',
        'requests'
    ],
    install_requires=[
        'requests'
    ],
    setup_requires=['pytest-runner'],
    tests_require=[
        'nose',
        'pytest',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],
)
