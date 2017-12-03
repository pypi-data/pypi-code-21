import os
from setuptools import setup, find_packages
with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='mailchimpworker',
    version='0.17',
    packages=['mailchimpworker'],
    install_requires=['Django==1.11.6', 'celery==4.1.0', 'redis==2.10.6'],
    include_package_data=True,
    license='MIT License',
    long_description=README,
    author='a_igin',
    author_email='a_igin@mail.ru',
)