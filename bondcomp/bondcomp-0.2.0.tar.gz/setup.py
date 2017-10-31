try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'name':'bondcomp',
    'version':'0.2.0',
    'description':'Bond benchmark suggestions.',
    'url':'https://github.com/rolfantlers',
    'author':'Anders Amundson',
    'author_email':'amundson@gmail.com',
    'license':'MIT',
    'install_requires':['nose','datetime'],
    'packages':['bondcomp'],
    'scripts':['bin/get_bench.py'],
}

setup(**config)
