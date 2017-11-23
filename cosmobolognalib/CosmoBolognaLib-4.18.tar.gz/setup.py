#!/usr/bin/env python

from setuptools import setup, Extension
import os
import platform

from distutils.sysconfig import get_config_vars

from setuptools.command.install import install

class InstallClass (install):

    def run (self):
        cwd = os.getcwd()
        dirb = cwd+"/build/"+os.listdir(cwd+"/build")[0]
        os.chdir("%s/CosmoBolognaLib/"%dirb)
        os.system("make CAMB")
        os.system("make CLASS")
        os.system("make MPTbreeze")
        os.system("make fftlog-f90")
        os.system("make mangle")
        os.system("make && make python")
        os.system("mv Python/CosmoBolognaLib.py ./")
        os.system("mv Python/_CosmoBolognaLib.so ./")
        os.system("echo 'from .CosmoBolognaLib import *' > __init__.py")
        os.system("rm -rf Catalogue Func Measure ReadParameters ChainMesh GlobalFunc LogNormal Modelling Statistics Cosmology Headers")
        os.chdir(cwd)
        install.run(self)


def readme():
    with open('README.rst') as f:
        return f.read()

setup(  name             = "CosmoBolognaLib",
        version          = "4.18",
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
