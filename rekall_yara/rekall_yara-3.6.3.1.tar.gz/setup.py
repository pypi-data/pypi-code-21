#
# Copyright (c) 2007-2013. The YARA Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import re
import os
import shutil
import posixpath
import platform
import subprocess
import sys

from setuptools import setup, Command, Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.sdist import sdist


args = sys.argv[1:]
macros = []

# The version of this package.
SUBVERSION = "1"


if '--with-profiling' in args:
    macros.append(('PROFILING_ENABLED', '1'))
    args.remove('--with-profiling')

def get_sources(source):
    result = []
    exclusions = set([
        "modules/cuckoo.c",
        "modules/magic.c",
        "modules/hash.c",
        "proc/linux.c",
        "proc/windows.c",
        "proc/mach.c",
    ])
    for directory, _, files in os.walk(source):
        for x in files:
            filename = posixpath.join(directory, x)
            if any([filename.endswith(ex) for ex in exclusions]):
                continue

            if x.endswith(".c"):
                result.append(filename)

    return result

rekall_yara_dir = os.path.dirname(__file__)

sources = [os.path.join(rekall_yara_dir,
                        "rekall_yara/yara-python/yara-python.c")]
sources += get_sources(os.path.join(rekall_yara_dir,
                                    "rekall_yara/yara/libyara/"))


def parse_version():
    """Create a version based on the yara version."""
    version = open(os.path.join(rekall_yara_dir,
                                "rekall_yara/version.txt")).read()
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", version)
    if m:
        return "%s.%s.%s.%s" % (m.group(1),
                                m.group(2),
                                m.group(3),
                                SUBVERSION)
    return version + SUBVERSION


class BuildExtCommand(build_ext):

    """Custom handler for the build_ext command."""

    project_builder = None

    def run(self):
        # Except on Windows we need to run the configure script.
        if platform.system() != "Windows":
            configure = os.path.join(
                rekall_yara_dir, "rekall_yara/yara/configure")
            if not os.path.exists(configure):
                subprocess.check_call(
                    ["/bin/sh", "./bootstrap.sh"],
                    cwd=os.path.join(rekall_yara_dir,
                                     "rekall_yara/yara/"))
            subprocess.check_call(
                ["/bin/sh", "./configure", "--without-crypto",
                 "--disable-magic", "--disable-cuckoo",
                 "--disable-dmalloc"],
                cwd=os.path.join(rekall_yara_dir,
                                 "rekall_yara/yara/"))

        build_ext.run(self)


class CleanCommand(Command):
    description = ("custom clean command that forcefully removes "
                   "dist/build directories")
    user_options = []
    def initialize_options(self):
        self.cwd = None
    def finalize_options(self):
        self.cwd = os.getcwd()
    def run(self):
        if os.getcwd() != self.cwd:
            raise RuntimeError('Must be in package root: %s' % self.cwd)

        for dirname in ['./build', './dist', 'rekall_yara.egg-info']:
            shutil.rmtree(dirname, True)


class Sdist(sdist):
    def run(self):
        # Make sure the tree is fully clean before we upload an sdist.
        subprocess.check_call(["./update.sh"])
        return sdist.run(self)


include_dirs = [
    os.path.join(rekall_yara_dir, 'rekall_yara/yara/yara-python'),
    os.path.join(rekall_yara_dir, 'rekall_yara/yara/libyara/include'),
    os.path.join(rekall_yara_dir, 'rekall_yara/yara/libyara/'),
    os.path.join(rekall_yara_dir, 'rekall_yara/yara/'),
]
libraries = []

if platform.system() == "Windows":
    # Python 2 on windows uses an ancient compiler which does not have
    # stdint. Python 3 uses VC14 which has a working stdint.h
    if sys.version_info[0] < 3:
        include_dirs.append("rekall_yara/windows/")

    libraries.append("advapi32")


setup(script_args=args,
      name='rekall_yara',
      url="http://www.rekall-forensic.com",
      long_description=open("README.txt").read(),
      cmdclass=dict(
          build_ext=BuildExtCommand,
          clean=CleanCommand,
          sdist=Sdist,
      ),
      version=parse_version(),
      packages=["rekall_yara"],
      author='Victor M. Alvarez',
      author_email='plusvic@gmail.com;vmalvarez@virustotal.com',
      zip_safe=False,
      ext_modules=[Extension(
          name='yara',
          sources=sources,
          libraries=libraries,
          include_dirs=include_dirs,
          define_macros=macros,
          extra_compile_args=['-std=gnu99']
      )])
