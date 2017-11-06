from setuptools import setup

import glob

setup(
    name = 'finoex',
    version = '0.16.0',
    # description = '',
    author = 'Fabian Peter Hammerle',
    author_email = 'fabian.hammerle@gmail.com',
    url = 'https://git.hammerle.me/fphammerle/finoex',
    download_url = 'https://git.hammerle.me/fphammerle/finoex/archive/0.14.1.tar.gz',
    keywords = ['finances'],
    # classifiers = [],
    packages = ['finoex'],
    # scripts = glob.glob('scripts/*'),
    install_requires = [
        'ioex>=0.17.0',
        'pytz',
        ],
    tests_require = ['pytest'],
    )
