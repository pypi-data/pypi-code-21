from setuptools import find_packages

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="adpix",
    description='Python client for adPix API services.',
    version='1.0',
    author='Surya Teja Cheedella',
    maintainer='Surya Teja Cheedella',
    maintainer_email='surya@snshine.in',
    url='http://adpix.snshine.in/',
    author_email='surya@snshine.in',
    install_requires=['requests==2.13.0'],
    packages=find_packages(),
    license="Apache 2.0"
)
