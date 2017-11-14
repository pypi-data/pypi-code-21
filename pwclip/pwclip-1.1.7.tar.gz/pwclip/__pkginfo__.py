#!/usr/bin/env python3
"""pwclip packaging information"""
from os import getcwd, path

name = distname = modname = 'pwclip'
numversion = (1, 1, 7)
version = '.'.join([str(num) for num in numversion])
provides = ['pwcli', 'pwclip', 'ykclip']
install_requires = [
    'argcomplete', 'netaddr', 'paramiko', 'psutil', 'pyusb',
    'python-gnupg', 'python-yubico', 'pyusb', 'PyYAML', 'wget']
lic = 'GPL'
description = "gui to temporarily save passwords to system-clipboard"
mailinglist = ""
author = 'Leon Pelzer'
author_email = 'mail@leonpelzer.de'
download_url = 'https://pypi.python.org/pypi/pwclip/%s#downloads'%version
classifiers = ['Environment :: Console',
               'Environment :: MacOS X',
               'Environment :: Win32 (MS Windows)',
               'Environment :: X11 Applications',
               'Intended Audience :: Developers',
               'Intended Audience :: End Users/Desktop',
               'Intended Audience :: System Administrators',
               'Intended Audience :: Information Technology',
               'License :: OSI Approved :: GNU General Public License (GPL)',
               'Operating System :: OS Independent',
               'Programming Language :: Python :: 3',
               'Topic :: Security',
               'Topic :: Utilities',
               'Topic :: Desktop Environment',
               'Topic :: System :: Systems Administration']
try:
	with open(path.join(getcwd(), 'CHANGELOG.rst'), 'r') as cfh:
		changelog = '\n\n\n'.join(cfh.read().split('\n\n\n')[:4])
	with open(path.join(getcwd(), 'README.rst'), 'r') as rfh:
		readme = rfh.read().format(ChangeLog=changelog)
	with open(path.join(getcwd(), 'README'), 'w+') as rfh:
		rfh.write(readme)
except OSError:
	readme = ''

long_desc = (readme)

entry_points = {
    'gui_scripts': ['pwclip = pwclip.__init__:pwclip',
                    'ykclip = pwclip.__init__:ykclip'],
    'console_scripts': ['pwcli = pwclip.__init__:pwcli']}
