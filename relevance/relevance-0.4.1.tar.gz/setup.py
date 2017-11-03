#!/usr/bin/python3

from setuptools import setup
from setuptools import find_packages

import relevance as main


setup(
    name=main.__name__,
    version=main.__version__,

    description=main.__doc__.split('\n')[1].strip(),
    long_description=main.__doc__.strip(),
    url='http://www.relevance.io',
    author='OverrideLogic',
    author_email='info@overridelogic.com',
    maintainer='Francis Lacroix',
    maintainer_email='f@overridelogic.com',

    license='MIT',
    platforms=['any'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search'
    ],

    packages=find_packages(exclude=['tests', 'tests.*']),
    provides=[main.__name__],

    python_requires='>=3.5',
    setup_requires=['flake8>=3.2.1'],
    tests_require=[],
    test_suite='tests',

    install_requires=[
        'Werkzeug>=0.12.2',
        'Flask>=0.12',
        'anyconfig>=0.9.1',
        'Twisted>=17.9.0',
        'python-dateutil>=2.6.1',
        'requests>=2.9.1',
    ],

    entry_points={
        'console_scripts': [
            'relevance=relevance.utils.cli:main',
            'relevance-server=relevance.utils.cli:server',
            'relevance-search=relevance.utils.cli:search',
        ],
    },

    data_files=[
        ('/etc/relevance', [
            'etc/search.json-example',
        ]),
    ],
)
