#!/usr/bin/env python
__author__ = 'Alexander Burdeinyi'

from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES
import os

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
package_dir = 'djangotworm'
# Tell distutils to put the data_files in platform-specific installation
# locations. See here for an explanation:
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

for dirpath, dirnames, filenames in os.walk(package_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.') or dirname == '__pycache__': del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

version = __import__('djangotworm').get_version()


def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='djangotworm',
    version='0.6.0',
    description="""Django QuerySets that can be Twisted aware. Adds several methods on a custom manager and queryset that return deferreds/coroutine/future.""",
    long_description=readme(),
    url='https://github.com/Bonus05/djangotworm',
    author='Alexander Burdeinyi',
    author_email='bonus05@gmail.com',
    download_url='https://github.com/Bonus05/djangotworm/raw/master/djangotworm-0.6.0.tar.gz',
    license='https://github.com/Bonus05/djangotworm/blob/master/MIT-LICENSE.txt',
    platform=['Any'],
    packages=packages,
    data_files = data_files,
    requires=['django', 'twisted',],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Python Modules',
   ],
    keywords='django orm twisted queryset async asyncio',
)
