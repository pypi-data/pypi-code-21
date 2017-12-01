import string
from setuptools import setup
from distutils.version import StrictVersion
from previous_version import PREVIOUS_VERSION
import subprocess
import os

# ~~~~~~ Compute version

# Add increment to Version class
def increment(self):
    parts = list(self.version)
    parts[-1] += 1
    string_repr = string.join(map(str, parts), '.')
    return StrictVersion(string_repr)


StrictVersion.increment = increment

# Get Spec version from Git
try:
    package_directory = os.path.dirname(os.path.abspath(__file__))
    spec_folder = os.path.join(package_directory, 'test', 'features', '.git')
    major_minor_version = subprocess.check_output(["git", "--git-dir", spec_folder, "describe", "--all"]).split('\n').pop(
            0).split("v").pop(1)
except BaseException as e:
    major_minor_version = "0.0"
    print "Unexpected error:", str(e)
# print "major_minor_version = " + str(major_minor_version)

# Compute next version
previous_version = StrictVersion(PREVIOUS_VERSION)
new_spec_version = StrictVersion("{0}.1".format(major_minor_version))
if new_spec_version > previous_version:
    current_version = new_spec_version
else:
    current_version = previous_version.increment()

# print "previous_version = ", previous_version
# print "current_version = ", current_version

# !!!!!!! MAJOR DEBT. This file is recompute every time the package is install
# VERSION = str(current_version)
VERSION = "0.19.2"

# ~~~~~ Create configuration

setup(
        name='tdl-client-python',
        packages=['tdl'],
        package_dir={'': 'src'},
        install_requires=['stomp.py==4.1.5'],
        version=VERSION,
        description='tdl-client-python',
        author='Tim Preece, Julian Ghionoiu',
        author_email='tdpreece@gmail.com, julian.ghionoiu@gmail.com',
        url='https://github.com/julianghionoiu/tdl-client-python',
        download_url='https://github.com/julianghionoiu/tdl-client-python/archive/v{0}.tar.gz'.format(VERSION),
        keywords=['kata', 'activemq', 'rpc'],
        classifiers=[],
)
