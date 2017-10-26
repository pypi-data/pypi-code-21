#!/usr/bin/env python

from distutils.core import setup
from setuptools import setup, find_packages

version = '0.1a6'

setup(
    name='versions-client',
    packages=find_packages(),
    version=version,
    description='Fetch software versions from your app for Prometheus.',
    long_description=open('README.rst').read(),
    author='Maikel Vlasman (Mediamoose)',
    author_email='maikel@mediamoose.nl',
    url='https://github.com/mediamoose/versions-client/tree/v{}'.format(version),
    download_url='https://github.com/mediamoose/versions-client/archive/v{}.tar.gz'.format(version),
    include_package_data=True,
    install_requires=[
        'envparse',
        'prometheus_client',
        'pyyaml',
    ],
    scripts=[
        'bin/os-package-versions',
    ],
    license='MIT',
    zip_safe=False,
    keywords=['versions-client', 'prometheus', 'versions', 'monitoring'],
    python_requires='>=2.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
