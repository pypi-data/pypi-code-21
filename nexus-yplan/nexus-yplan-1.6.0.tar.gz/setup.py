# -*- encoding:utf-8 -*-
import codecs
import os
import re

from setuptools import find_packages, setup


def get_version(filename):
    with codecs.open(filename, 'r', 'utf-8') as fp:
        contents = fp.read()
    return re.search(r"__version__ = ['\"]([^'\"]+)['\"]", contents).group(1)


version = get_version(os.path.join('nexus', '__init__.py'))

with codecs.open('README.rst', 'r', 'utf-8') as readme_file:
    readme = readme_file.read()

with codecs.open('HISTORY.rst', 'r', 'utf-8') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

setup(
    name='nexus-yplan',
    version=version,
    author='Disqus',
    author_email='opensource@disqus.com',
    maintainer='YPlan',
    maintainer_email='adam@yplanapp.com',
    url='https://github.com/yplan/nexus',
    description=(
        'Nexus is a pluggable admin application in Django. '
        'It\'s designed to give you a simple design and architecture for building admin applications.'
    ),
    long_description=readme + '\n\n' + history,
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    install_requires=[],
    license='Apache License 2.0',
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development'
    ],
)
