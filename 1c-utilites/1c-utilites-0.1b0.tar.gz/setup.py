import os
from setuptools import find_packages, setup
from utilites_1c import __version__ as prog_version


RMF = os.path.join(os.path.dirname(__file__), 'README.rst')
with open(RMF) as readme:
    README = readme.read()


def load_requirements(file_name):
    with open(os.path.join(os.path.dirname(__file__), file_name)) as req_file:
        return req_file.read().strip().split('\n')


REQUIRES = load_requirements('requirements.txt')


setup(
    name='1c-utilites',
    version=prog_version,
    packages=find_packages(),
    url='',
    license='AGPL+',
    author='Sergey Klyukov',
    author_email='onegreyonewhite@mail.ru',
    description='Utilites for maintenance 1C services',
    long_description=README,
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities',
    ],
    entry_points={
        'console_scripts': ['1c-utilites=utilites_1c.manager:main'],
    },
    install_requires=[
    ] + REQUIRES,
)
