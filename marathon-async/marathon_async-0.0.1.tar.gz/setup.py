# !/usr/bin/env python
from setuptools import setup

setup(
    name='marathon_async',
    version='0.0.1',
    description='Async Marathon Client Library',
    long_description="""Python interface to the Mesos Marathon REST API with asyncio support.""",
    author='Ivan Bovyrin',
    author_email='ibovirin@gmail.com',
    install_requires=['aiohttp==2.2.5', 'marathon==0.9.3'],
    url='https://github.com/ibovyrin/aio-marathon-python',
    packages=['marathon_async'],
    platforms='Posix; MacOS X; Windows',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
