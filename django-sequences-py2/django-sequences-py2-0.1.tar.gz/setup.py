from __future__ import unicode_literals

import codecs
import os.path

import setuptools

root_dir = os.path.abspath(os.path.dirname(__file__))

description = "Forked from augustien's django-sequences, this package aims to maintain py2 compatibility."
with codecs.open(os.path.join(root_dir, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='django-sequences-py2',
    version='0.1',
    description=description,
    long_description=long_description,
    url='https://github.com/flocklet/django-sequences-py2',
    author='Aymeric Augustin, Flocklet Technologies',
    author_email='opensource@flocklet.com',
    license='BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    packages=[
        'sequences',
        'sequences.migrations',
    ],
)
