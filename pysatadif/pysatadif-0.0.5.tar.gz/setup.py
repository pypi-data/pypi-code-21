from setuptools import setup
from codecs import open
from os import path, walk

here = path.abspath(path.dirname(__file__))

datadir = path.join('pysatadif', 'data')
datafiles = [(d, [path.join(d, f) for f in files])
             for d, folders, files in walk(datadir)]
print(datafiles)

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pysatadif',
    version='0.0.5',

    description='Simple utility to generate proper ADIF for satellite contacts',
    long_description=long_description,

    url='https://github.com/jeremymturner/pysatadif',

    author='Jeremy Turner',
    author_email='jeremy@jeremymturner.com',

    # Choose your license
    license='Apache',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    # What does your project relate to?
    keywords='hamradio satellites adif',

    packages=['pysatadif'],
    include_package_data=True,

    data_files=datafiles,

    install_requires=['jinja2'],

    entry_points={
        'console_scripts': [
            'pysatadif=pysatadif.pysatadif:main',
        ],
    },
)
