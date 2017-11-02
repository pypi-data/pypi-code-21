from __future__ import print_function

import warnings
from setuptools import setup, find_packages, Extension
from setuptools.command.install import install

class angle_install(install):
    def run(self):
        print("please type `install`.\n")
        mode = None
        return install.run(self)

cmdclass = {}
ext_modules = []
cmdclass.update({'install': angle_install})

setup(
    cmdclass=cmdclass,
    ext_modules=ext_modules,
    name='Netbase',
    version="0.1.23",
    author="Pannous",
    author_email="info@pannous.com",
    # https://github.com/pannous/netbase
    packages=find_packages(),
    description='Netbase : Wikidata World Graph',
    license='Apache2 license',
    long_description=open('README.md', 'rb').read().decode('utf8'),
    dependency_links=['git+http://github.com/pannous/netbase.git#egg=angle'],
    install_requires=['dill'],
    scripts=[],#'netbase.py'],
    package_data={
        # '': ['*.cu', '*.cuh', '*.h'],
    },
)
