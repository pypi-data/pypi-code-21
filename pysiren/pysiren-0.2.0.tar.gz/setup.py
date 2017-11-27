from setuptools import setup, find_packages

__author__ = 'Michal Dziemianko'
__pkg_name__ = 'pysiren'

version = '0.2.0'

setup(
    author=__author__,
    author_email='michal.dziemianko@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    description='Utility for generating Siren Hypermedia compliant payloads.',
    extras_require={
        'docs': [
            'sphinx'
        ]
    },
    install_requires=[
        'typing'
    ],
    keywords='REST HATEOAS Hypermedia RESTful SIREN HAL API JSONAPI web framework',
    name='pysiren',
    packages=find_packages(include=['pysiren', 'pysiren.*']),
    tests_require=[
        'nose',
        'hypothesis'
    ],
    test_suite="test",
    url='https://github.com/mdziemianko/pysiren',
    version=version
)