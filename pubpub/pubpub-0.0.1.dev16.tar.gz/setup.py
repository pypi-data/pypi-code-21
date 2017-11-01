#!/usr/bin/env python

from setuptools import setup

setup(
    setup_requires=['pbr>=1.9', 'setuptools>=17.1'],
    pbr=True,
    entry_points='''
        [console_scripts]
        pubpub=pubpub.cli.pubpub:cli
    ''',
)

# setup(
#     name='pubpub',
#     version=pkg_vars['__version__'],
#     setup_requires=['pbr>=1.9', 'setuptools>=17.1'],
#     pbr=True,
#     packages=find_packages(),
#     include_package_data=True,
#     install_requires=[
#         'Click',
#     ],
# )
