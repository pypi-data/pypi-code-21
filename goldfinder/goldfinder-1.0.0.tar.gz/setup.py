from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='goldfinder',
    version='1.0.0',

    description='''App for locating materials in the Brandeis Goldfarb and Farber libraries''',
    # rst is some bull shit and i will not be party to it. markdown or die
    long_description='https://github.com/9999years/goldfinder/blob/master/readme.md',
    url='https://github.com/9999years/goldfinder',
    author='Rebecca Turner',
    author_email='637275@gmail.com',
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Utilities',
        'Natural Language :: English',
    ],

    keywords='library brandeis',

    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'cdctables']),

    entry_points={
        'console_scripts': [
            'goldfinder = goldfinder.goldfinder:main',
        ],
    },

    install_requires=[
        'requests',
        'lxml',
        'cssselect',
    ]
)
