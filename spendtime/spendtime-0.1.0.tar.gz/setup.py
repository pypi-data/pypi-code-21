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
                'rm -vrf ./build ./dist ./*.pyc ./*tgz ./*.egg-info *.rst *.db *~'
            )

setup(name = 'spendtime',
      version = '0.1.0',
      description = 'Simple timetracking tool for the terminal',
      long_description = readme(),
      classifiers = [
          'Development Status :: 4 - Beta',
          'Intended Audience :: End Users/Desktop',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Programming Language :: Python :: 3',
          'Topic :: Utilities'
      ],
      url = 'https://github.com/morngrar/spendtime',
      author = 'Svein-Kåre Bjørnsen',
      author_email = 'sveinkare@gmail.com',
      license = 'GPL',
      include_package_data = True,
      packages = find_packages(),
      install_requires = [
          "ui>=0.1.4",
      ],
      entry_points = {
          'console_scripts': [
              'spendtime = spendtime.commands:main'
          ]
      },
      cmdclass = {
          'clean': CleanCommand,
      },
      zip_safe = False
)
