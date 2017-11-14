from os import path

from setuptools import setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst')) as f:
    long_description = f.read()

with open(path.join(here, 'VERSION')) as f:
    version = f.read().strip()

with open('requirements.txt') as f:
    requirements = f.read().split()

with open(path.join(here, 'requirements-tests.txt')) as f:
    test_requirements = f.read()

setup(
    version=version,
    name='wsgiauth0',
    description='Auth0 middleware for multiple client configurations',
    long_description=long_description,
    packages=['wsgiauth0'],
    install_requires=requirements,
    tests_require=test_requirements,
    url='https://gitlab.com/dialogue/wsgiauth0',
    license='MIT',
    entry_points={
        'paste.filter_app_factory': [
            'middleware = wsgiauth0:factory',
        ]
    },
    extras_require={
        'dynamodb': ["boto3~=1.4"],
    }
)
