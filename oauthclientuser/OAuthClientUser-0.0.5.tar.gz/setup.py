# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="OAuthClientUser",
    version='0.0.5',
    description='A User Authenticate APP for OAuth2 of django-oauth-toolkit',
    long_description=long_description,

    url='https://github.com/lixujia/OAuthClientUser',
    author='Xujia Li',
    author_email='lixujia.cn@gmail.com',

    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP :: Session',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='Django OAuth2 Authenticate UserData',
    packages=find_packages(),
    install_requires=['django', 'djangorestframework'],
)
