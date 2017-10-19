import versioneer
from setuptools import find_packages, setup

setup(
    name='fusion-util',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='Utility package for Fusion',
    url='https://github.com/fusionapp/fusion-util',
    install_requires=[
        'Twisted[tls] >= 15.0.0',
        'incremental',
        'testtools >= 2.1.0',
        ],
    license='MIT',
    packages=find_packages(),
    include_package_data=True)
