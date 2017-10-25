#!/usr/bin/env python

from setuptools import setup


setup(
    name='quikkly-python-sdk',
    packages=['quikklysdk'],
    scripts=['scripts/quikkly-generate-svg.py', 'scripts/quikkly-scan-image.py'],
    version='1.0.2',
    description='Quikkly Python SDK',
    long_description=open('README.md').read(),
    author='Mattias Linnap',
    author_email='mattias@linnap.com',
    url='https://quikklycodes.com/',
    license='Proprietary',
    install_requires=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Operating System :: MacOS',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Image Recognition',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
