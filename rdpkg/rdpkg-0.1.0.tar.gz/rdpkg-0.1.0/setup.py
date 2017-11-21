from setuptools import setup, find_packages

setup(
    name='rdpkg',
    version='0.1.0',
    packages=find_packages(),
    scripts=['rdpkg'],

    author='James Neill',
    author_email='jneill542@gmail.com',
    description='Installs Debian packages from remote URLs',
    license='Apache License 2.0',
    keywords='dpkg',
    url='https://github.com/jmsnll/rdpkg'
)
