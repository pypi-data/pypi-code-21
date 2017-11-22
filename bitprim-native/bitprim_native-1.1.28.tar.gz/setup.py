#!/usr/bin/env python

# 
# Copyright (c) 2017 Bitprim developers (see AUTHORS)
# 
# This file is part of Bitprim.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 

import glob
import os
import platform
import shutil
import stat
import sys

from setuptools import setup, find_packages
from setuptools.extension import Extension
from distutils import dir_util, file_util
from distutils import log
from setuptools.command.install_lib import install_lib
from setuptools.command.install import install
from setuptools.command.develop import develop
# from setuptools.command.egg_info import egg_info
from setuptools.command.build_ext import build_ext

from distutils.command.build import build
from setuptools.command.install import install

from setuptools.dist import Distribution
from conans.client.conan_api import (Conan, default_manifest_folder)
import fnmatch

from sys import platform

PKG_NAME = 'bitprim_native'
# VERSION = '1.1.9'
SYSTEM = sys.platform



def get_similar_lib(path, pattern):
    # for file in os.listdir('.'):
    #     if fnmatch.fnmatch(file, '*.txt'):
    #         print file
    for file in os.listdir(path):
        if fnmatch.fnmatch(file, pattern):
            return file
    return ""


# if platform == "linux" or platform == "linux2":
#     # linux
# elif platform == "darwin":
#     # OS X
# elif platform == "win32":
#     # Windows...

def get_libraries():
    # libraries = ['bitprim-node-cint', 'bitprim-node', 'bitprim-blockchain', 'bitprim-network', 'bitprim-consensus', 'bitprim-database', 'bitprim-core', 'boost_atomic', 'boost_chrono', 'boost_date_time', 'boost_filesystem', 'boost_iostreams', 'boost_locale', 'boost_log', 'boost_log_setup', 'boost_program_options', 'boost_random', 'boost_regex', 'boost_system', 'boost_unit_test_framework', 'boost_prg_exec_monitor', 'boost_test_exec_monitor', 'boost_thread', 'boost_timer', 'secp256k1', 'bz2', 'gmp', 'z',]
    fixed = ['bitprim-node-cint', 'bitprim-node', 'bitprim-blockchain', 'bitprim-network', 'bitprim-consensus', 'bitprim-database', 'bitprim-core']

    if platform == "win32":
        libraries = ['boost_atomic', 'boost_chrono', 'boost_date_time', 'boost_filesystem', 'boost_iostreams', 'boost_locale', 'boost_log', 'boost_log_setup', 'boost_program_options', 'boost_random', 'boost_regex', 'boost_system', 'boost_unit_test_framework', 'boost_prg_exec_monitor', 'boost_test_exec_monitor', 'boost_thread', 'boost_timer', 'secp256k1', 'bz2', 'mpir', 'z',]
        winlibs = fixed
        for lib in libraries:
            # print(lib)
            xxx = get_similar_lib('bitprim/lib', "*" + lib + "*")
            if xxx != '':
                xxx = xxx.replace('.lib', '')
                # print(xxx)
                winlibs.append(xxx)
    
        # print(winlibs)
        return winlibs
    else:
        libraries = ['boost_atomic', 'boost_chrono', 'boost_date_time', 'boost_filesystem', 'boost_iostreams', 'boost_locale', 'boost_log', 'boost_log_setup', 'boost_program_options', 'boost_random', 'boost_regex', 'boost_system', 'boost_unit_test_framework', 'boost_prg_exec_monitor', 'boost_test_exec_monitor', 'boost_thread', 'boost_timer', 'secp256k1', 'bz2', 'gmp', 'z',]
        return fixed + libraries

def do_conan_stuff(microarch=None):

    # if not microarch:
    #     microarch = 'x86_64'

    print('do_conan_stuff microarch')
    print(microarch)

    # New API in Conan 0.28
    c, _, _ = Conan.factory()

    try:
        # c.remote_add(remote, url, verify_ssl, args.insert)
        c.remote_add('bitprim', 'https://api.bintray.com/conan/bitprim/bitprim')
    except:
        print ("Conan Remote exists, ignoring exception")

    refe = "."

    if microarch:
        # c.install(refe, verify=None, manifests=None)
        opts = ['*:microarchitecture=%s' % (microarch,)]
        c.install(refe, verify=None, manifests_interactive=None, manifests=None, options=opts)
    else:
        c.install(refe, verify=None, manifests_interactive=None, manifests=None)
    

def do_build_stuff(microarch=None):

    print('*********************************************************************************************************')
    print(os.path.dirname(os.path.abspath(__file__)))
    print(os.getcwd())
    print('*********************************************************************************************************')

    prev_dir = os.getcwd()

    do_conan_stuff(microarch)

    print('*********************************************************************************************************')
    print(os.path.dirname(os.path.abspath(__file__)))
    print(os.getcwd())
    print('*********************************************************************************************************')

    os.chdir(prev_dir) 

    print('*********************************************************************************************************')
    print(os.path.dirname(os.path.abspath(__file__)))
    print(os.getcwd())
    print('*********************************************************************************************************')


    # libraries = ['bitprim-node-cint', 'bitprim-node', 'bitprim-blockchain', 'bitprim-network', 'bitprim-consensus', 'bitprim-database', 'bitprim-core', 'boost_atomic', 'boost_chrono', 'boost_date_time', 'boost_filesystem', 'boost_iostreams', 'boost_locale', 'boost_log', 'boost_log_setup', 'boost_program_options', 'boost_random', 'boost_regex', 'boost_system', 'boost_unit_test_framework', 'boost_prg_exec_monitor', 'boost_test_exec_monitor', 'boost_thread', 'boost_timer', 'secp256k1', 'bz2', 'gmp', 'z',],
    # libraries = get_libraries()
    extensions[0].libraries = get_libraries()
    

class DevelopCommand(develop):
    user_options = develop.user_options + [
        ('microarch=', None, 'CPU microarchitecture')
    ]

    def initialize_options(self):
        develop.initialize_options(self)
        self.microarch = None

    def finalize_options(self):
        develop.finalize_options(self)

    def run(self):
        global microarch
        microarch = self.microarch

        print('*********************************** DevelopCommand run microarch')
        print(microarch)

        do_build_stuff(microarch)

        develop.run(self)



class InstallCommand(install):
    user_options = install.user_options + [
        ('microarch=', None, 'CPU microarchitecture')
    ]

    def initialize_options(self):
        install.initialize_options(self)
        self.microarch = None

    def finalize_options(self):
        install.finalize_options(self)

    def run(self):
        global microarch
        microarch = self.microarch

        print('*********************************** InstallCommand run microarch')
        print(microarch)

        do_build_stuff(microarch)


        install.run(self)


class BuildCommand(build):
    user_options = build.user_options + [
        ('microarch=', None, 'CPU microarchitecture')
    ]

    def initialize_options(self):
        build.initialize_options(self)
        self.microarch = None

    def finalize_options(self):
        build.finalize_options(self)

    def run(self):
        global microarch
        microarch = self.microarch

        print('--------------------------------------- BuildCommand run microarch')
        print(microarch)

        do_build_stuff(microarch)


        build.run(self)


# ------------------------------------------------

microarch = ''


extensions = [
	Extension('bitprim_native',

        define_macros = [('BITPRIM_LIB_STATIC', None),],

    	sources = ['utils.c',  'chain/header.c', 'chain/block.c', 'chain/merkle_block.c', 'bitprimmodule.cpp',
        'chain/chain.c', 'binary.c', 'chain/point.c', 'chain/history.c', 'chain/word_list.c', 
        'chain/transaction.c', 'chain/output.c', 'chain/output_list.c',  'chain/input.c', 'chain/input_list.c', 
        'chain/script.c', 'chain/payment_address.c', 'chain/compact_block.c', 'chain/output_point.c',
        'chain/block_list.c', 'chain/transaction_list.c', 'chain/stealth_compact.c', 'chain/stealth_compact_list.c'],

        include_dirs=['bitprim/include'],
        library_dirs=['bitprim/lib'],
        # libraries = ['bitprim-node-cint', 'bitprim-node', 'bitprim-blockchain', 'bitprim-network', 'bitprim-consensus', 'bitprim-database', 'bitprim-core', 'boost_atomic', 'boost_chrono', 'boost_date_time', 'boost_filesystem', 'boost_iostreams', 'boost_locale', 'boost_log', 'boost_log_setup', 'boost_program_options', 'boost_random', 'boost_regex', 'boost_system', 'boost_unit_test_framework', 'boost_prg_exec_monitor', 'boost_test_exec_monitor', 'boost_thread', 'boost_timer', 'secp256k1', 'bz2', 'gmp', 'z',],
        # libraries = get_libraries()
    ),
]



exec(open('./version.py').read())
setup(
    name=PKG_NAME,
    # version=VERSION,
    version=__version__,
    

    description='Bitprim Platform',
    long_description='Bitprim Platform',
    url='https://github.com/bitprim/bitprim-py',

    # Author details
    author='Bitprim Inc',				#TODO!
    author_email='dev@bitprim.org',		#TODO!

    # Choose your license
    license='MIT',    					#TODO!

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        'Programming Language :: C++',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    # What does your project relate to?
    keywords='bitcoin litecoin cash money bitprim',

    # # You can just specify the packages manually here if your project is
    # # simple. Or you can use find_packages().
    # packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    # packages=['bitprim-node-cint'],
    # # package_dir={'bitprim-node-cint': 'src/mypkg'},
    # package_dir={'bitprim-node-cint': './'},
    # package_data={'bitprim-node-cint': ['bitprim/lib/*bitprim-node-cint.*']},
    # packages=('bitprim', ),
    # package_data={ 'bitprim': ['bitprim/lib/*bitprim-node-cint*'] },

    # packages=['bitprim-node-cint'],
    # package_data={ 'bitprim-node-cint': ['libbitprim-node-cint.so'] },

    # distclass = MyDist,

    # eager_resources=['bitprim/lib/libbitprim-node-cint.so'],

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # # List run-time dependencies here.  These will be installed by pip when
    # # your project is installed. For an analysis of "install_requires" vs pip's
    # # requirements files see:
    # # https://packaging.python.org/en/latest/requirements.html
    # install_requires=['peppercorn'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },

#   data_files = [('lib\\site-packages',['C:\\development\\bitprim\\build\\bitprim-node-cint\\bitprim-node-cint.dll'])],

	# data_files = [('lib\\site-packages', ['bitprim-node-cint\\lib\\bitprim-node-cint.dll'])],
    # data_files = [
    #     ('lib/site-packages', ['bitprim-node-cint/lib/bitprim-node-cint.*'])
    # ],

    # data_files = [
    #     ('lib/site-packages', glob.glob('bitprim-node-cint/lib/*bitprim-node-cint.*'))
    # ],


    # data_files = [
    #     ('/usr/local/lib', glob.glob('bitprim/lib/*bitprim-node-cint.*'))
    # ],


# tion="-I/home/fernando/dev/bitprim/bitprim-node-cint/include" --global-option="-L/home/fernando/dev/bitprim/build/bitprim-node-cint" -e .

    ext_modules = extensions,


    # cmdclass=dict(
    #     install_lib=CustomInstall,
    #     # install=CustomInstallCommand,
    # ),

    # cmdclass = {'build_ext': build_ext_subclass },


    cmdclass={
        'build': BuildCommand,
        'install': InstallCommand,
        'develop': DevelopCommand,
        # 'egg_info': EggInfoCommand,
        
    },

)





# class CustomInstallCommand(install):
#     """Customized setuptools install command - prints a friendly greeting."""
#     def run(self):
#         print "Hello, developer, how are you? :)"
#         install.run(self)

# class CustomInstall(install_lib):
#     def install(self):
#         print('CustomInstall.install')
#         install_lib.install(self)

#         build_ext = self.get_finalized_command('build_ext')
        

#         for key in build_ext.compiler.executables.keys():
#             # self.set_executable(key, build_ext.compiler.executables[key])
#             print("executables - key: %s, value: %s" % (key, build_ext.compiler.executables[key]))

# class build_ext_subclass( build_ext ):
#     def build_extensions(self):

#         print("build_ext_subclass.build_extensions")
#         print("self.compiler.compiler_type")
#         print(self.compiler.compiler_type)

#         for key in self.compiler.executables.keys():
#             print("executables - key: %s, value: %s" % (key, self.compiler.executables[key]))

#         # c = self.compiler.compiler_type
#         # if copt.has_key(c):
#         #    for e in self.extensions:
#         #        e.extra_compile_args = copt[ c ]
#         # if lopt.has_key(c):
#         #     for e in self.extensions:
#         #         e.extra_link_args = lopt[ c ]
#         build_ext.build_extensions(self)

# class CustomInstall(install_lib):
#     def install(self):
#         print('CustomInstall.install')
#         install_lib.install(self)
#         bitprim_install_dir = os.path.join(self.install_dir, 'bitprim/')
        
#         if not os.path.exists(bitprim_install_dir):
#             os.makedirs(bitprim_install_dir)

#         log.info("bitprim_install_dir: %s" % (bitprim_install_dir, ))
#         log.debug("bitprim_install_dir: %s" % (bitprim_install_dir, ))
#         print("bitprim_install_dir: %s" % (bitprim_install_dir, ))

#         for lib_file in SETUP_DATA_FILES:
#             log.info("lib_file: %s" % (lib_file, ))
#             log.debug("lib_file: %s" % (lib_file, ))
#             print("lib_file: %s" % (lib_file, ))

#             filename = os.path.basename(lib_file)
#             log.info("filename: %s" % (filename, ))
#             log.debug("filename: %s" % (filename, ))
#             print("filename: %s" % (filename, ))

#             dest_file = os.path.join(self.install_dir, 'bitprim', filename)

#             log.info("dest_file: %s" % (dest_file, ))
#             log.debug("dest_file: %s" % (dest_file, ))
#             print("dest_file: %s" % (dest_file, ))

#             # file_util.copy_file(lib_file, bitprim_install_dir)
#             file_util.copy_file(lib_file, dest_file)

# class MyDist(Distribution):
#      def has_ext_modules(self):
#          return True
