# coding=utf-8
import os
from setuptools import setup


def __path(filename):
    return os.path.join(os.path.dirname(__file__), filename)

build = str(int(os.environ['PIP_BUILD']) + 300)
keywords = os.environ['PIP_KEYWORDS']

version = '0.{}'.format(build)

setup(
    name='missinglink-sdk',
    version=version,
    description='SDK for streaming realtime metrics to https://missinglink.ai',
    author='MissingLink.ai',
    author_email='support+sdk@missinglink.ai',
    platforms=['any'],
    license='mit',
    packages=['missinglink'],
    keywords=keywords,
    install_requires=[
        'missinglink-kernel=={}'.format(version),
    ]
)
