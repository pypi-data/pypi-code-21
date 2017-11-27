import os, sys
from setuptools import setup, Extension

# Author: wayne@thebubbleworks.com

from distutils.command.clean import clean
from distutils.core import Command
from distutils.dir_util import remove_tree

# bleson/VERSION file must follow: https://www.python.org/dev/peps/pep-0440/

version_file = open('VERSION')
version = version_file.read().strip()

# support overriding version from env
version=os.getenv('MODULE_VERSION', version)

if not version:
    raise ValueError("Version not set")

print("Version={}".format(version))

class SimpleCommand(Command):
    # default some Command abstract class boilerplate for subclasses
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


class SuperClean(clean):

    def run(self):
        self.all = True
        super().run()
        # remove_tree doesn't ignore errors. liek it says it should..
        paths = ['sdist', 'dist', 'Release', 'Debug', 'x64', 'Generated Files' ]
        for path in paths:
            if os.path.exists(path):
                remove_tree(path)


class Tag(SimpleCommand):

    def run(self):
        rc = os.system("git tag -a RELEASE_%s -m 'Release version %s'" % (version, version))
        if rc != 0:
            sys.exit(rc)
        rc = os.system("git push --tags")
        sys.exit(rc>>8)


class Publish(SimpleCommand):

    def run(self):
        # TODO: use a Pythonic method
        upload_cmd = "twine upload dist/*"
        rc = os.system(upload_cmd)
        sys.exit(rc>>8)


blesonwin_module = Extension('blesonwin',                              
                             sources = ['blesonwin.cpp'],
                             extra_compile_args = ["/std:c++latest"], 
                             )

setup(name = 'blesonwin', 
    version = version,
    description = 'Windows 10 WinRT Extension for BluetoothLE',
    license='MIT',
    author='TheCellule',
    author_email='thecellule@gmail.com',
    url='https://github.com/TheCellule/blesonwin',
    test_suite='tests',
    cmdclass={
      'clean': SuperClean,
      'publish': Publish,
      'tag': Tag,
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.5'
    ],
    ext_modules = [blesonwin_module],
)