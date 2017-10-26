# ============================================================
#
# Copyright (C) 2011 by Johannes Wienke <jwienke at techfak dot uni-bielefeld dot de>
#
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation;
# either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# ============================================================

from setuptools import setup
from setuptools import find_packages
from setuptools import Command

class PrintOutputs(Command):
    """
    Prints out the generated output names.

    @author: jwienke
    """

    user_options = []
    description = "Prints the generated output names."

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        c = self.get_finalized_command('bdist_egg')
        for o in c.get_outputs():
            print("##### %s" % o)

setup(name='rstsandbox',
      version='0.16.5',
      description="Robotics Systems Types - Sandbox",
      author='Johannes Wienke',
      author_email='jwienke@techfak.uni-bielefeld.de',
      license="GPLv3",
      url="https://code.cor-lab.org/projects/rst",

      packages=find_packages(exclude=['build', 'rst.*', 'rst']),

      install_requires=['protobuf==3.3.2'],

      cmdclass={'print_outputs': PrintOutputs})
