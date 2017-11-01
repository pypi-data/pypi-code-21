from setuptools import setup, find_packages

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='flapjack_stack',
    version='1.0.0',
    description='A multi-layered approach to settings',
    long_description=long_description,
    author='Jason Myers',
    author_email='jason.myers@juiceanalytics.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        'PyYaml==3.12'
    ],
    url='https://github.com/juiceinc/flapjack_stack',
    keywords='settings flapjack_stack',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    license='License :: OSI Approved :: MIT License',

)
