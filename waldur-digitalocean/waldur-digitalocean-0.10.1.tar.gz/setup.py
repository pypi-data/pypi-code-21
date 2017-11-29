#!/usr/bin/env python
from setuptools import setup, find_packages


dev_requires = [
    'Sphinx==1.2.2',
]

tests_requires = [
    'factory_boy==2.4.1',
    'mock>=1.0.1',
]

install_requires = [
    'nodeconductor>0.148.3',
    'python-digitalocean>=1.5',
]


setup(
    name='waldur-digitalocean',
    version='0.10.1',
    author='OpenNode Team',
    author_email='info@opennodecloud.com',
    url='http://waldur.com',
    description='Waldur plugin for managing DigitalOcean resources.',
    long_description=open('README.rst').read(),
    license='MIT',
    package_dir={'': 'src'},
    packages=find_packages('src', exclude=['*.tests', '*.tests.*', 'tests.*', 'tests']),
    install_requires=install_requires,
    zip_safe=False,
    extras_require={
        'tests': tests_requires,
        'dev': dev_requires,
    },
    entry_points={
        'nodeconductor_extensions': (
            'waldur_digitalocean = waldur_digitalocean.extension:DigitalOceanExtension',
        ),
    },
    tests_require=tests_requires,
    include_package_data=True,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
