from setuptools import setup, find_packages
import os
from io import open


packagename = 'post-qa'
description = 'Upload QA metrics for LSST Data Management.'
author = 'Jonathan Sick'
author_email = 'jsick@lsst.org'
license = 'MIT'
url = 'https://github.com/lsst-sqre/post-qa'
version = '1.3.3'


def read(filename):
    full_filename = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        filename)
    return open(full_filename, mode='r', encoding='utf-8').read()

long_description = read('README.rst')


setup(
    name=packagename,
    version=version,
    description=description,
    long_description=long_description,
    url=url,
    author=author,
    author_email=author_email,
    license=license,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='lsst',
    packages=find_packages(exclude=['docs', 'tests*', 'data']),
    install_requires=['future>=0.15.2',
                      'requests>=2.10.0',
                      'GitPython>=2.0.3',
                      'pytz>=2016.4',
                      'pyyaml>=3.12',
                      'jsonschema>=2.5.1',
                      'rfc3987==1.3.7',
                      'strict-rfc3339==0.7'],
    tests_require=['pytest', 'pytest-cov', 'pytest-flake8',
                   'pytest-mock', 'responses'],
    package_data={'postqa': ['schemas/*.json']},
    entry_points={
        'console_scripts': [
            'post-qa = postqa.cli:run_post_qa',
        ]
    }
)
