from datetime import datetime
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

# Notes to myself. Yohei 2017-06-20, 2017-08-21
#
# Run this script by typing one of the following lines (without the # signs) in Windows Command Prompt.
#
# (0) To save a copy of the package in c:\codes\source\dist\
# cd c:\codes\source
# python setup.py sdist
# (0 - alternative) To save a copy of the package in c:\codes\source\dist\
# Double-click archive_yomo_for_myself.bat under C:\codes
# (0 - alternative) To save a copy of the package in c:\codes\source\dist\
# Double-click archive_yomo_for_PyPI_and_myself.bat under C:\codes
#
# (1) To save a copy of the package and upload it to the PyPi test site 
# cd c:\codes\source
# python setup.py sdist upload -r pypitest
# 
# (2) To save a copy of the package and upload it to the PyPi Live site 
# cd c:\codes\source
# python setup.py sdist upload
# 
# Note that the options (1) and (2) rely on the contents of the .pypirc file and require one-time registration with PyPi. The .pypirc file is located under c:\Users\YS. The one-time registration was done on the Windows Command Prompt by typing: (1) python setup.py register -r pypitest and (2) python setup.py register. Some recommend twine for upload. Some recommend testing before uploading.
# 
# I am using Python 3.6.0 on Windows 10. Python -v returns:
# Python 3.6.0 |Anaconda custom (64-bit)| (default, Dec 23 2016, 11:57:41) [MSC v.1900 64 bit (AMD64)] on win32
