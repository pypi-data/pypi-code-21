# coding: utf-8

"""
    See README.md for details
"""


import sys
from setuptools import setup, find_packages

NAME = "nifi-python-swagger-client"
VERSION = "1.2.0"

with open('test-requirements.txt') as test_reqs_file:
    test_requirements = test_reqs_file.read()

with open('requirements.txt') as reqs_file:
    requirements = reqs_file.read()

setup(
    name=NAME,
    version=VERSION,
    description="Swagger 2.0 client in python for Apache NiFi Rest API",
    author="Daniel Chaffelson",
    author_email="chaffelson@gmail.com",
    url="https://nifi.apache.org/",
    download_url='https://github.com/Chaffelson/nifi-python-swagger-client'
                 '/archive/' + VERSION + '.tar.gz',
    keywords=["Swagger", "NiFi Rest Api", "Python"],
    install_requires=requirements,
    packages=find_packages(
        include=['swagger_client',
                 'swagger_client.apis',
                 'swagger_client.models'],
        exclude=['*.tests', '*.tests.*', 'tests.*', 'tests',
                 'swagger_client_tests']
    ),
    include_package_data=True,
    license="Apache Software License 2.0",
    long_description="""\
    The Rest Api provides programmatic access to command and control a NiFi 
    instance in real time. Start and stop processors, monitor queues, query 
    provenance data, and more. Each endpoint below includes a description, 
    definitions of the expected input and output, potential response codes, 
    and the authorizations required to invoke each service.
    """,
    tests_require=test_requirements,
    setup_requires=test_requirements,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='test',
)
