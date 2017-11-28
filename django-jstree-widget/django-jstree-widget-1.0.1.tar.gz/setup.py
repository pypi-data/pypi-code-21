from __future__ import unicode_literals

from setuptools import setup, find_packages

from jstree import __version__

with open('LICENSE', 'r') as license_file:
    license_data = license_file.read()

setup(
    name='django-jstree-widget',
    version=__version__,
    packages=find_packages(),
    author='Jean-Etienne Castagnede',
    author_email='j.e.castagnede@gmail.com',
    license=license_data,
    description='Customizable widget to serve jstree with django.',
)
