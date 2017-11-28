#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The Screen class lets you to do positioned writes to the dos terminal.
The Screen class also allows you to specify the colors for foreground and
background, to the extent the dos terminal allows.
"""

classifiers = """\
Development Status :: 5 - Production/Stable
Environment :: Win32 (MS Windows)
Intended Audience :: Developers
License :: OSI Approved :: BSD License
Operating System :: Microsoft :: MS-DOS
Operating System :: POSIX :: Linux
Programming Language :: Python
Topic :: Software Development :: Libraries
Topic :: System :: Shells
Topic :: Terminals
"""

from setuptools import setup

doclines = __doc__.split('\n')

setup(
    name='dosbox-screen',
    version='1.1.1',
    requires=['colorama'],
    install_requires=['colorama'],
    description=doclines[0],
    classifiers=[line for line in classifiers.split('\n') if line],
    long_description=open('README.rst').read(),
    license="BSD",
    author='Bjorn Pettersen',
    author_email='bjorn@tkbe.org',
    url='https://github.com/thebjorn/doscmd-screen',
    download_url='https://github.com/thebjorn/doscmd-screen',
    py_modules=['screen']
)
