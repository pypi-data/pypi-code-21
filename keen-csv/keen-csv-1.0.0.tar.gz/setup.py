import os
from setuptools import setup

setup_path = os.path.dirname(__file__)
reqs_file = open(os.path.join(setup_path, 'requirements.txt'), 'r')
reqs = reqs_file.readlines()
reqs_file.close()

setup(
    name='keen-csv',
    description='Builds a multiline CSV string from a Keen IO response',
    version='1.0.0',
    license='MIT',
    author='Jevon Wild',
    author_email='jevon@keen.io',
    url='https://github.com/dorkusprime/keen-csv.py',
    install_requires=reqs,
    packages=['keen_csv']
)
