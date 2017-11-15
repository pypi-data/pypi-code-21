#!/usr/bin/env python

from setuptools import setup, Extension
import os
import platform

from distutils.sysconfig import get_config_vars

from setuptools.command.install import install

class InstallClass (install):

    SYS = ""
    if platform.system()=='Darwin':
        SYS = "SYS=MAC"

    def run (self):
        cwd = os.getcwd()
        dirb = cwd+"/build/"+os.listdir(cwd+"/build")[0]
        os.chdir("%s/CosmoBolognaLib/"%dirb)
        os.system("make CAMB")
        os.system("make CLASS")
        os.system("make MPTbreeze")
        os.system("make fftlog-f90")
        os.system("make mangle")
        os.system("make %s && make python %s"%(self.SYS, self.SYS))
        os.system("mv Python/CosmoBolognaLib/__init__.py ./")
        os.system("cp Python/CosmoBolognaLib/CosmoBolognaLib.py ./")
        os.system("cp Python/CosmoBolognaLib/_CosmoBolognaLib.so ./")
        os.chdir(cwd)
        install.run(self)


def readme():
    with open('README.rst') as f:
        return f.read()

setup(  name             = "CosmoBolognaLib",
        version          = "4.12",
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
