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

setup(name = 'ui',
      version = '0.1.4',
      description = 'Simple menu-driven user interface for the terminal',
      long_description = readme(),
      classifiers = [
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Programming Language :: Python :: 3',
          'Topic :: Software Development :: User Interfaces'
      ],
      url = 'https://github.com/morngrar/ui',
      author = 'Svein-Kåre Bjørnsen',
      author_email = 'sveinkare@gmail.com',
      license = 'GPL',
      include_package_data = True,
      packages = find_packages(),
      cmdclass = {
          'clean': CleanCommand,
      },
      zip_safe = False
)
