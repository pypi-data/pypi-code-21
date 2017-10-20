from setuptools import setup, find_packages

setup(
    name='pyadxcli',
    version='0.1',
    description='A basic client to Audionamix API',
    url='https://github.com/audionamix/pyadxcli',
    author='Audionamix',
    author_email='guillaume.vincke@audionamix.com',

    packages=find_packages(exclude=['tests']),
    install_requires=[
        'requests>=2.18.4'
    ]
)
