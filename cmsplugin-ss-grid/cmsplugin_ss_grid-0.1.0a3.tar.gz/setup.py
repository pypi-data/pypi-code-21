from setuptools import setup, find_packages
from codecs import open
from os import path
import cmsplugin_ss_grid

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='cmsplugin_ss_grid',
    version=cmsplugin_ss_grid.__version__,

    description='Bootstrap grid plugin for djangocms',
    long_description=long_description,

    url='https://github.com/alexjbartlett/cmsplugin-ss-grid',

    # Author details
    author='Alex J Bartlett',
    author_email='alex@sourceshaper.com',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    # What does your project relate to?
    keywords='djangocms bootstrap grid',

    packages=find_packages(),
    include_package_data=True,

    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, <4',
    # install_requires=['django-cms>3.0,<=3.4.4',],

)
