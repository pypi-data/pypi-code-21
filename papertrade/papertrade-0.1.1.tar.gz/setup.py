#!/usr/bin/python3

import os
from setuptools import setup, find_packages, Command

def readme():
    os.system("pandoc --from=markdown --to=rst --output=README.rst README.md")
    with open('README.rst') as f:   # has to be in .rst format
        return f.read()

class CleanCommand(Command):
    """Custom clean command to tidy up the project root"""
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        if os.name == "posix":
            os.system(
                'rm -vrf ./build ./dist ./*.pyc ./*tgz ./*.egg-info *.rst'
            )

setup(name = 'papertrade',
      version = '0.1.1',
      description = 'Simple paper trading application for the terminal.',
      long_description = readme(),
      classifiers = [
          'Development Status :: 3 - Alpha',
          'Intended Audience :: End Users/Desktop',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Programming Language :: Python :: 3 :: Only',
          'Topic :: Utilities'
      ],
      url = 'https://github.com/morngrar/papertrade',
      author = 'Svein-Kåre Bjørnsen',
      author_email = 'sveinkare@gmail.com',
      license = 'GPL',
      include_package_data = True,
      packages = find_packages(),
      install_requires = [
          "yahoo-finance>=1.4.0",
          "ui>=0.1.3",
      ],
      entry_points = {
          'console_scripts': [
              'papertrade = papertrade.commands:main'
          ]
      },
      cmdclass = {
          'clean': CleanCommand,
      },
      zip_safe = False
)
