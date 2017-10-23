from setuptools import setup
from codecs import open
from os import path
import sys

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'optionloop', '_version.py')) as version_file:
    exec(version_file.read())

with open(path.join(here, 'README.md'), 'rt') as readme_file:
    readme = readme_file.read()

desc = readme
try:
    import pypandoc
    long_description = pypandoc.convert_text(desc, 'rst', format='md')
    with open(path.join(here, 'README.rst'), 'w') as rst_readme:
        rst_readme.write(long_description)
except (ImportError, OSError, IOError):
    print('Warning: pypandoc module not found, could not convert Markdown to RST')
    long_description = desc

install_requires = [
    'six'
]

tests_require = [
    'nose',
]

setup(
    name='optionloop',
    version=__version__,
    description='Allows collapsing of nested for loops via dictionary iteration',
    long_description=long_description,
    url='https://github.com/arghdos/optionLoop',
    author='arghdos',
    author_email='arghdos@gmail.com',
    license='GPL',
    packages=['optionloop', 'optionloop.tests'],
    zip_safe=True,
    test_suite='nose.collector',
    install_requires=install_requires,
    tests_require=tests_require,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
