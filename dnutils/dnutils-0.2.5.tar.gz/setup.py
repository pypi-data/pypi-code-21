import os
from distutils.core import setup

import sys
import _version

__basedir__ = _version.__basedir__
__version__ = _version.__version__


def basedir(name):
    return os.path.join(__basedir__, name)


with open(os.path.join(os.path.dirname(__file__), __basedir__, 'requirements.txt'), 'r') as f:
    requirements = [l.strip() for l in f.readlines() if l.strip()]


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='dnutils',
    packages=['dnutils', 'dnutils._version'],
    package_dir={
        'dnutils': basedir('dnutils'),
        'dnutils._version': '_version',
    },
    version=__version__,
    description='A collection of convenience tools for everyday Python programming',
    long_description=read('README.md'),
    author='Daniel Nyga',
    author_email='daniel.nyga@t-online.de',
    url='https://spritinio.de/dnutils',
    download_url='https://github.com/danielnyga/dnutils/archive/%s.tar.gz' % __version__,
    keywords=['testing', 'logging', 'threading', 'multithreading', 'debugging', 'tools', 'utilities'],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Logging',
        'Topic :: Utilities',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    install_requires=requirements,
)
