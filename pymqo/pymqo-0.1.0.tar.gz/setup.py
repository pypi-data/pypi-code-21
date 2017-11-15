from setuptools import setup, find_packages
from pymqo import __version__, __author__, __email__

setup(
    name='pymqo',
    version=__version__,
    packages=find_packages(),
    install_requires=[
        'pika==0.11.0'
    ],
    url='https://github.com/ducminhgd/pymqo',
    license='',
    author=__author__,
    author_email=__email__,
    description='Python Message Queue Object'
)
