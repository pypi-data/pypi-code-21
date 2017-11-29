from inspect import cleandoc

from setuptools import setup

_version = {}
execfile('spleen/_version.py', _version)

setup(
    name = 'Spleen',
    packages = ['spleen',],
    version = _version['__version__'],
    description = 'idk fix later',
    author = 'Bright.md',
    author_email = 'cory@bright.md',
    url = 'https://github.com/Brightmd/Spleen',
    keywords = [],
    classifiers = [],
    scripts = [],
    install_requires=cleandoc('''
        attrs
        ''').split()
)
