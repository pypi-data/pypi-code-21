
from setuptools import setup, find_packages

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

version = None

with open("version.txt", "r+") as f:
    version = f.read()

    setup(
        name='asf_hyp3',
        version=str(version),

        description='Api for ASF\'s hyp3 system',
        long_description=long_description,

        url='https://github.com/asfadmin/hyp3-api',

        author='ASF Student Development Team 2017',
        author_email='eng.accts@asf.alaska.edu',

        license="License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",

        classifiers=['Development Status :: 3 - Alpha',

                     # Indicate who your project is intended for
                     'Intended Audience :: Science/Research',
                     'Topic :: Scientific/Engineering :: GIS',

                     # Specify the Python versions you support here. In particular, ensure
                     # that you indicate whether you support Python 2, Python 3 or both.
                     'Programming Language :: Python :: 2.7',
                     'Programming Language :: Python :: 3.4',
                     ],
        keywords='hyp3 api hyp3-api asf',

        packages=find_packages(),
        package_data={
            'asf_hyp3': ['messages.json']
        },

        install_requires=['requests>=2.14.0', 'pyshp>=1.2.11', 'pygeoif>=0.7']
    )
