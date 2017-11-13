from distutils.core import setup
from setuptools import setup, find_packages
setup(
    name = 'plytype',
    version = '0.5.0',
    keywords = ('python', 'lexer', 'parser'),
    description = 'PLY with get_type and set_type',
    license = 'MIT License',

    author = 'Jian Wang',
    author_email = 'yt4766269@126.com',

    packages = find_packages(),
    platforms = 'linux',
)
