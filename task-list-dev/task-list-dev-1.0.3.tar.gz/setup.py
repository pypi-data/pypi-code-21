# coding: utf-8

import os
from setuptools import find_packages, setup

# allow setup.py to be run from any path
file_abs = os.path.abspath(__file__)
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


def get_context(filename):
    with open(os.path.join(os.path.dirname(file_abs), filename)) as f:
        return f.read()


def version(*args, **kwargs):
    latest = args[0]
    with open(os.path.join(os.path.dirname(file_abs), 'VERSION'), 'w+') as f:
        f.write(latest)
        f.close()
    return latest


app = __import__('task_list_dev')


setup(
    name='task-list-dev',
    version='1.0.3',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='List tools developement',
    long_description=get_context('README.md'),
    url=app.__url__,
    author=app.__author__,
    author_email=app.__email__,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
