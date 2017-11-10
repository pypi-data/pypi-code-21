import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

setup(
    name='django-restresp',
    version='0.1.1',
    packages=['restresp'],
    description='Pseudo-standard responders for django DRF',
    long_description=README,
    author='Andrea Carmisciano',
    author_email='andrea.carmisciano@gmail.com',
    url='https://github.com/acarmisc/django-restresp/',
    license='MIT',
    install_requires=[
        'Django>=1.9',
	'djangorestframework',
    ]
)
