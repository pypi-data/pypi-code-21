import re
from distutils.core import setup
from setuptools import find_packages

VERSIONFILE="helputils/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

setup(
    name="helputils",
    version=verstr,
    author="eayin2",
    author_email="eayin2@gmail.com",
    packages=find_packages(),
    url="https://github.com/eayin2/helputils",
    description="Bunch of random useful functions and classes",
    install_requires=["pymongo", "Pillow", "requests"],
    extras_require = {
        "sendmails": ["gymail"]
    }
)
