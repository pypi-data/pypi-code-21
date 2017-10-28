from codecs import open
from os import path

from pip.req import parse_requirements
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'LICENSE.txt'), encoding='utf-8') as f:
    license = f.read()


def read_requirements(location, file):
    reqs_path = path.join(location, file)
    install_reqs = parse_requirements(reqs_path, session='hack')
    reqs = [str(ir.req) for ir in install_reqs]
    return reqs


setup(
    name='almanac-bot',
    version='0.0.2',
    description='Almanac Bot for Twitter',
    long_description=long_description,
    author='Julio C. Barrera',
    author_email='logoff@logoff.cat',
    url='https://github.com/logoff/almanac-bot',
    license=license,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Information Technology',
        'Topic :: Sociology :: History',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Framework :: Sphinx'
    ],
    keywords='twitter history',
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=read_requirements(here, 'real-requirements.txt'),
    extra_requires={
        'dev': read_requirements(here, 'real-dev-requirements.txt')
    }

)
