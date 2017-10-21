from setuptools import setup, find_packages
from snapp_email.api_client import PACKAGE_VERSION

setup(
    name='SnappEmailApiClient',
    packages=find_packages(),
    version=PACKAGE_VERSION,
    description='Python API Client for Snapp Email',
    author='Snapp.Email',
    author_email='info@marg.si',
    url='https://github.com/4thOffice/ApiClient.py',
    download_url='https://github.com/4thOffice/ApiClient.py/tarball/v' + PACKAGE_VERSION,
    keywords=['api', 'client'],
    classifiers=[],
    install_requires=['requests'],
)
