import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-dantejsoncoder',
    version='0.1',
    packages=['dantejsoncoder'],
    include_package_data=True,
    license='GNU General Public License v3.0', 
    description='A simple Django app to covert standard django-models to json',
    long_description=README,
    url='https://github.com/DanteOnline/django-dantejsoncoder',
    author='DanteOnline',
    author_email='iamdanteonline@gmail.com'
)