from setuptools import setup
import re

# version control
# after https://stackoverflow.com/questions/458550/standard-way-to-embed-version-into-python-package
VERSIONFILE="yomo/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))
    
setup(name='yomo',
      version=verstr,
      author='Yohei Shinozuka',
      author_email='Yohei.Shinozuka@nasa.gov',
      packages=['yomo'],
)
