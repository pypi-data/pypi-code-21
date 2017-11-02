from setuptools import setup

setup(
    name='crtsh',
    author='PaulSec',
    version='0.1.0',
    packages='.',
    description='(Unofficial) Python API for https://crt.sh',
    install_requires=["bs4", "requests"],
    url = 'https://github.com/PaulSec/crt.sh',
    download_url = 'https://github.com/PaulSec/crt.sh/archive/0.1.0.tar.gz',
    keywords = ['crt.sh', 'ssl', 'certificates', 'osint'],
)