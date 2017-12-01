import os
from setuptools import setup

README = """
See the README on `GitHub
<https://github.com/uw-it-aca/uw-restclients-coda>`_.
"""

# The VERSION file is created by travis-ci, based on the tag name
version_path = 'uw_coda/VERSION'
VERSION = open(os.path.join(os.path.dirname(__file__), version_path)).read()
VERSION = VERSION.replace("\n", "")

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

url = "https://github.com/uw-it-aca/uw-restclients-coda"
setup(
    name='UW-RestClients-CoDa',
    version=VERSION,
    packages=['uw_coda'],
    author="UW-IT AXDD",
    author_email="aca-it@uw.edu",
    include_package_data=True,
    install_requires=['commonconf>=0.6',
                      'uw-restclients-core'],
    license='Apache License, Version 2.0',
    description=('A restclient for accessing the Instructor Course Dashboards'
                 'application at the University of Washington'),
    long_description=README,
    url=url,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ],
)


