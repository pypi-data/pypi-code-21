"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""
from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

exec(open('src/tinysumma/version.py').read())

setup(
    name='tinysumma',
    version=__version__,
    description='Summarize tinyletter statistics',
    long_description=long_description,
    url='https://github.com/awbirdsall/tinysumma',
    author='Adam Birdsall',
    author_email='abirdsall@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    keywords=['newsletter', 'tinyletter', 'command line', 'cli'],
    package_dir = {'': 'src'},
    packages=['tinysumma'],
    install_requires=['pandas', 'tinyapi'],
    package_data={
        'tinysumma': ['data/messages.csv', 'data/urls.csv']
    },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'tinysumma=tinysumma.main:command',
        ],
    },
)
