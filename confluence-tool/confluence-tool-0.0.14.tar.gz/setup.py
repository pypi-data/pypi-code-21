#!/usr/bin/env python

from distutils.core import setup

setup(
    name='confluence-tool',
    version='0.0.14',
    description='Confluence API and CLI',
    author='Kay-Uwe (Kiwi) Lorenz',
    author_email='kiwi@franka.dyndns.org',
    install_requires=[
            'requests',
            'keyring',
            'keyrings.alt',
            'html5print',
            'pyquery',
            'pyaml',
            'pystache',
            'argdeco'
        ],
    url='https://github.com/klorenz/python-confluence-tool',
    packages=['confluence_tool', 'confluence_tool.cli', ],
    package_data = {
        'confluence_tool': ['templates/*.mustache', 'templates/*.html']
    },
    include_package_data = True,

    entry_points = dict(
        console_scripts = [
            'ct = confluence_tool:main',
            'confluence-tool = confluence_tool:main',
        ]
    ),
    license="MIT",
    )
