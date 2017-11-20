#!/usr/bin/env python
"""
 Copyright (C) 2016 by SolarWinds, LLC.
 All rights reserved.
"""

import sys
import subprocess
from setuptools import setup, Extension
from distutils.command.build import build
from setuptools.command.install import install
from setuptools.command.sdist import sdist

version = '2.0.2'


def python_version_supported():
    if sys.version_info[0] == 2:
        if sys.version_info[1] not in (6, 7):
            return False
    elif sys.version_info[0] == 3:
        if sys.version_info[1] < 3:
            return False
    return True


def os_supported():
    return sys.platform.startswith('linux')


if not (python_version_supported() and os_supported()):
    sys.exit('This package supports only Python 2.6, 2.7, 3.3 and above on Linux.')

ext_modules = [Extension('appoptics.swig._oboe',
                         sources=['appoptics/swig/oboe_wrap.cxx'],
                         depends=['appoptics/swig/oboe.hpp'],
                         include_dirs=['appoptics/swig', 'appoptics'],
                         libraries=['oboe-1.0', 'rt'],
                         library_dirs=['appoptics/swig'],
                         runtime_library_dirs=['$ORIGIN']), ]


class CustomBuild(build):
    def run(self):
        cmd = ['make', 'wrapper']
        try:
            subprocess.check_output(cmd)
        except:
            pass
        self.run_command('build_ext')
        build.run(self)


class CustomInstall(install):
    def run(self):
        cmd = ['make', 'download-all']
        try:
            subprocess.check_output(cmd)
        except:
            pass
        self.run_command('build_ext')
        install.run(self)

class CustomSdist(sdist):
    def run(self):
        cmd = ['make', 'download-all']
        try:
            subprocess.check_output(cmd)
        except:
            pass
        self.run_command('build_ext')
        sdist.run(self)


try:
    import pypandoc
    rst_long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    # fail "gracefully"
    rst_long_description = open('README.md').read()

setup(name='appoptics',
      cmdclass={'build': CustomBuild, 'install': CustomInstall, 'sdist': CustomSdist},
      version=version,
      author='SolarWinds, LLC',
      author_email='support@appoptics.com',
      url='https://www.appoptics.com/monitor/python-performance',
      download_url='https://pypi.python.org/pypi/appoptics',
      description='AppOptics libraries, instrumentation, and web middleware components '
                  'for WSGI, Django, and Tornado.',
      long_description=rst_long_description,
      keywords='appoptics traceview tracelytics oboe liboboe instrumentation performance wsgi middleware django',
      ext_modules=ext_modules,
      packages=['appoptics', 'appoptics.swig'],
      package_data={'appoptics': ['swig/liboboe-1.0.so.0']},
      license='LICENSE.txt',
      install_requires=['decorator', 'six'],
      )
