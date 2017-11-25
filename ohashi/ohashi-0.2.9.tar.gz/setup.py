#/usr/bin/env python
import codecs
import os

from setuptools import setup, find_packages

read = lambda filepath: codecs.open(filepath, 'r', 'utf-8').read()

# Load package meta from the pkgmeta module without loading the package.
pkgmeta = {}
pkgmeta_file = os.path.join(os.path.dirname(__file__), 'ohashi', 'pkgmeta.py')
with open(pkgmeta_file) as f:
    code = compile(f.read(), 'pkgmeta.py', 'exec')
    exec(code, pkgmeta)

setup(
    name='ohashi',
    version=pkgmeta['__version__'],
    description='Yet another opinionated utilities kit for Django projects.',
    author=pkgmeta['__author__'],
    author_email='bryan@hello-base.com',
    license='BSD',
    url='http://github.com/hello-base/ohashi',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'django>=1.4.1',
        'redis>=2.6.0',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities'
    ]
)
