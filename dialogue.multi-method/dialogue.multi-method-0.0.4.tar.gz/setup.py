from os import path

from setuptools import find_packages, setup


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst')) as f:
    long_description = f.read()

with open(path.join(here, 'VERSION')) as f:
    version = f.read().strip()

setup(
    name='dialogue.multi-method',
    version=version,
    maintainer='Hugo Duncan',
    maintainer_email='hugo.duncan@dialogue.co',
    url='https://github.com/dialoguemd/multi-method',
    long_description=long_description,
    packages=['dialogue.multi_method'],
    install_requires=[
    ],
    extras_require={
        'dev': [
            'pytest',
            'pytest-watch',
        ],
        'packaging': [
            'bumpversion',
            'twine',
        ],
        'test': [
            'flake8-import-order',
            'pylama',
            'pytest',
            'pytest-cov',
            'tox',
        ],
    },
)
