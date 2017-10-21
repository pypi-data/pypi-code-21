from setuptools import setup, find_packages

setup(
    name='simple_table',
    version='0.0.2',
    description='A very very very basic terminal table.',
    url='https://github.com/Frederick-S/simple-table',
    packages=find_packages(exclude=['tests']),
    test_suite="tests"
)
