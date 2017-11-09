from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
"""
python setup.py sdist
python setup.py bdist_wheel --universal
twine upload dist/*
"""
setup(
    name='postquick-py',
    version='1.0.6',
    description='PostQuick Python client',
    long_description='PostQuick Python client',
    url='',
    author='Startnet Co',
    author_email='',
    license='GNU General Public License v2 (GPLv2)',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='websocket real-time pubsub',
    packages=['postquick'],
    install_requires=['socketIO-client-nexus'],
    extras_require={},
    package_data={},
    data_files=[],
)
