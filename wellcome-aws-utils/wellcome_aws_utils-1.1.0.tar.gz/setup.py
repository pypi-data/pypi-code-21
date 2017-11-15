# -*- encoding: utf-8 -*-

import os

from setuptools import find_packages, setup


def local_file(name):
    return os.path.relpath(os.path.join(os.path.dirname(__file__), name))


SOURCE = local_file('src')
README = local_file('README.rst')


# Assignment to placate pyflakes. The actual version is from the exec that
# follows.
__version__ = None

with open(local_file('src/wellcome_aws_utils/version.py')) as o:
    exec(o.read())

assert __version__ is not None


setup(
    name='wellcome_aws_utils',
    packages=find_packages(SOURCE),
    package_dir={'': SOURCE},
    version=__version__,
    install_requires=[
        'boto3',
        'daiquiri',
        'python-dateutil',
    ],
    python_requires='>=3.6',
    description='A collection of AWS utilities',
    long_description=open(README).read(),
    author='Wellcome Trust (Digital Platform Team)',
    author_email='wellcomedigitalplatform@wellcome.ac.uk',
    url='https://github.com/wellcometrust/aws_utils',
    keywords=['aws'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development',
        'Topic :: Utilities',
    ],
)
