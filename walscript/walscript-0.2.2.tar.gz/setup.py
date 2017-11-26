'''
setup.py for walscript
'''
import os
import sys
from shutil import copyfile
from setuptools import setup, find_packages
from distutils.core import setup
from distutils.command.install import install as _install


class install(_install):
    def run(self):
        _install.run(self)
        cwd = os.getcwd()
        wal = '/walscript/wal.py'
        dest = '/usr/local/bin/wal'

        print('running postinstall from ' + cwd)
        try:
            copyfile(cwd + wal, dest)
            print('copied ' + cwd + wal + ' to ' + dest)
        except IOError as e:
            if (e[0] == errno.EPERM):
                print('could not copy' + 
                      cwd + wal + ' to ' + dest)
        try:
            os.chmod('/usr/local/bin/wal', 0o755)
            print('set file permissions to 755')
        except IOError as e:
            if (e[0] == errno.EPERM):
                print('could not set file permissions ' +
                  ' on ' + dest + ' to 755')

setup(
    name = 'walscript',
    version = '0.2.2',
    description = 'web automation layer',
    long_description = (
        'a browser automation tool with a yaml front end '
        'and selenium/python/phantomjs bacd end'),
    author = 'Kolby',
    author_email = 'kolby@fasterdevops.com',
    license = 'MIT',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
	'Operating System :: POSIX',
	'Operating System :: POSIX :: Linux',
	'Operating System :: Unix',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
	'Topic :: Internet'],
    keywords = 'web automation layer',
    install_requires = [
        'PyYAML==3.12',
        'selenium==2.53.2',
        'simplejson==3.10.0',
        'six==1.10.0',
        'urllib3==1.15.1'],
    url = 'https://fasterdevops.github.io/',
    download_url = 'https://github.com/classmember/wal/archive/master.zip',
    packages=['walscript'],
    package_dir={'walscript': 'walscript'},
    cmdclass={'install': install}
)
