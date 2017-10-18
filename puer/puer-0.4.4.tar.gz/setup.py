from setuptools import setup, find_packages
from os.path import join, dirname
import puer

setup(
    name='puer',
    version=puer.__version__,
    packages=find_packages(exclude=('./venv',)),
    long_description=open(join(dirname(__file__), 'README.txt')).read(),
    entry_points={
        'console_scripts': [
            'puer_init = puer.puer_init:main'
        ]
    },
    install_requires=[
        'aiohttp',
        'pyyaml',
    ]
)