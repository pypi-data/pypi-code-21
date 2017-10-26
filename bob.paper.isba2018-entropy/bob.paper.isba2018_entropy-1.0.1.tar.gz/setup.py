#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

from setuptools import setup, dist
dist.Distribution(dict(setup_requires = ['bob.extension']))

# load the requirements.txt for additional requirements
from bob.extension.utils import load_requirements, find_packages
install_requires = load_requirements()

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    # This is the basic information about your project. Modify all this
    # information before releasing code publicly.
    name = 'bob.paper.isba2018_entropy',
    version = '1.0.1',
    description = 'Calculating the entropy of fingervein patterns',

    url = 'https://gitlab.idiap.ch/bob/bob.paper.isba2018_entropy',
    license = 'GPLv3',
    author = 'Vedrana Krivokuca',
    author_email = 'vedrana.krivokuca@idiap.ch',
    keywords = 'bob, fingervein recognition, entropy',

    # If you have a better, long description of your package, place it on the
    # 'doc' directory and then hook it here
    long_description = open('README.rst').read(),

    # This line is required for any distutils based packaging.
    # It will find all package-data inside the 'bob' directory.
    packages = find_packages('bob'),
    include_package_data = True,

    # This line defines which packages should be installed when you "install"
    # this package. All packages that are mentioned here, but are not installed
    # on the current system will be installed locally and only visible to the
    # scripts of this package. Don't worry - You won't need administrative
    # privileges when using buildout.
    install_requires = install_requires,

    # This entry defines which scripts you will have inside the 'bin' directory
    # once you install the package (or run 'bin/buildout'). The order of each
    # entry under 'console_scripts' is like this:
    #   script-name-at-bin-directory = module.at.your.library:function
    #
    # The module.at.your.library is the python file within your library, using
    # the python syntax for directories (i.e., a '.' instead of '/' or '\').
    # This syntax also omits the '.py' extension of the filename. So, a file
    # installed under 'example/foo.py' that contains a function which
    # implements the 'main()' function of particular script you want to have
    # should be referred as 'example.foo:main'.
    #
    # In this simple example we will create a single program that will print
    # the version of bob.
    entry_points = {

     # configurations should be declared using this entry:
     'bob.bio.config': [
        'utfvp-mc = bob.paper.isba2018_entropy.configurations.utfvp_mc',    # MC extractor for images from UTFVP database
        'utfvp-rlt = bob.paper.isba2018_entropy.configurations.utfvp_rlt',  # RLT extractor for images from UTFVP database
        'utfvp-wld = bob.paper.isba2018_entropy.configurations.utfvp_wld',  # WLD extractor for images from UTFVP database
        'vera-mc = bob.paper.isba2018_entropy.configurations.vera_mc',      # MC extractor for images from VERA database
        'vera-rlt = bob.paper.isba2018_entropy.configurations.vera_rlt',    # RLT extractor for images from VERA database
        'vera-wld = bob.paper.isba2018_entropy.configurations.vera_wld',    # WLD extractor for images from VERA database
        ],

      # scripts should be declared using this entry:
      'console_scripts' : [
        'calculate_entropy.py = bob.paper.isba2018_entropy.scripts.calculate_entropy:main',  # Script that calculates entropy of fingervein patterns
      ],
    },

    # Classifiers are important if you plan to distribute this package through
    # PyPI. You can find the complete list of classifiers that are valid and
    # useful here (http://pypi.python.org/pypi?%3Aaction=list_classifiers).
    classifiers = [
      'Framework :: Bob',
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
)