from setuptools import setup

setup(
    name='dfskit',
    version='0.0.1',
    description='A suite of utilities for converting and working with data serialization formats',
    long_description=open('README.rst').read(),
    author='James Ridgway',
    url='https://github.com/jamesridgway/dsfkit',
    license='MIT',
    packages=[
        'dsfkit',
        'dsfkit.cli',
        'dsfkit.utilities'
    ],
    entry_points={
        'console_scripts': [
            'csvjson = dsfkit.cli.csvjson:main'
        ]
    }
)
