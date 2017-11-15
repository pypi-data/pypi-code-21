#!/usr/bin/env python

from setuptools import setup, Extension
import os
import platform

from distutils.sysconfig import get_config_vars

from setuptools.command.install import install

class InstallClass (install):

    SYS =""
    if platform.system()=='Darwin':
        SYS="SYS=MAC"

    def run (self):
        os.system("cd CosmoBolognaLib && make CAMB && cd - ")
        os.system("cd CosmoBolognaLib && make CLASS && cd - ")
        os.system("cd CosmoBolognaLib && make MPTbreeze && cd - ")
        os.system("cd CosmoBolognaLib && make fftlog-f90 && cd - ")
        os.system("cd CosmoBolognaLib && make mangle && cd - ")
        os.system("cd CosmoBolognaLib && make venice && cd - ")
        os.system("cd CosmoBolognaLib && make ALL %s && make python %s && cd - "%(self.SYS, self.SYS))
        os.system("mv CosmoBolognaLib/Python/CosmoBolognaLib/__init__.py CosmoBolognaLib/")
        os.system("cp CosmoBolognaLib/Python/CosmoBolognaLib/CosmoBolognaLib.py CosmoBolognaLib/")
        os.system("cp CosmoBolognaLib/Python/CosmoBolognaLib/_CosmoBolognaLib.so CosmoBolognaLib/")
        install.run(self)


def readme():
    with open('README.rst') as f:
        return f.read()

setup(  name             = "CosmoBolognaLib",
        version          = "4.1",
        description      = "C++ libraries for cosmological calculations",
        long_description = readme(),
        author           = "Federico Marulli",
        author_email     = "federico.marulli3@unibo.it",
        url              = "http://github.com/federicomarulli/CosmoBolognaLib",
        license          = "GNU General Public License",
        zip_safe         = False,
        include_package_data = True,
        packages         = ["CosmoBolognaLib"],
        package_data     = {"CosmoBolognaLib" : ["_CosmoBolognaLib.so"]},
        cmdclass         = {'install': InstallClass} )
