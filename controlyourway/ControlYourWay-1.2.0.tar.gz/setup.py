from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ControlYourWay',
    version='1.2.0',
    description='Control Your Way Python Library',
    long_description=long_description,
    url='https://www.controlyourway.com/Resources/PythonLibraryHelp',
    author='Hubert Jetschko',
    author_email='hubert@controlyourway.com',
    license='Other/Proprietary License',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Communications',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='IoT, Internet of Things communication platform',
    install_requires=['websocket-client'],
    packages=['ControlYourWay_p27', 'ControlYourWay_p3'],
)