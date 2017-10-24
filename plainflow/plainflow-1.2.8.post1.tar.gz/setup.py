
import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# Don't import plainflow module here, since deps may not be installed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'plainflow'))
from version import VERSION

long_description = '''
This is the official Python client for Plainflow (https://www.plainflow.com).

Documentation and more details at https://www.plainflow.com/docs/developers/sdk/python
'''

install_requires = [
    "requests>=2.7,<3.0",
    "six>=1.5",
    "python-dateutil>2.1"
]

setup(
    name='plainflow',
    version=VERSION,
    url='https://github.com/plainflow-dcp/plainflow-python',
    author='Plainflow',
    author_email='friends@plainflow.com',
    maintainer='Plainflow',
    maintainer_email='friends@plainflow.com',
    test_suite='plainflow.test.all',
    packages=['plainflow', 'plainflow.test'],
    license='MIT License',
    install_requires=install_requires,
    description='The official Python client for Plainflow.',
    long_description=long_description,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
)
