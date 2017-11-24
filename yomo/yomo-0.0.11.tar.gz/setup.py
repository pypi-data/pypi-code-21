from setuptools import setup
import re

package = 'yomo'
# version from _verion.py, after https://stackoverflow.com/questions/458550/standard-way-to-embed-version-into-python-package
VERSIONFILE=package+"/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))
# other meta-data from README.rst
READMEFILE="README.rst"
readme = open(READMEFILE, "rt").read()
descriptionstr = readme.splitlines()[4].strip()
moduleauthor = readme.splitlines()[8]
author = moduleauthor[len('.. moduleauthor:: '):moduleauthor.find('<')-1]
email = moduleauthor[moduleauthor.find('<')+1:moduleauthor.rfind('>')] 
# the summary
setup(name=package,
      version=verstr,
      author=author,
      author_email=email,
      description=descriptionstr,
      url='https://pypi.python.org/pypi/'+package+'/',
      license='MIT',
      packages=[package],
      long_description=readme,
      classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
      ],
)
