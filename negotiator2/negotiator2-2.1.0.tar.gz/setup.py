"""Setup for negotiator2."""
from setuptools import setup
import re

# Extract version number from code. Be very strict about the
# format of the version string as a extra sanity check.
VERSIONFILE = "negotiator2/__init__.py"
verfilestr = open(VERSIONFILE, "rt").read()
match = re.search(r"^__version__ = '(\d\.\d.\d+(\.\d+)?)'",
                  verfilestr, re.MULTILINE)
if match:
    version = match.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE))


setup(
    name='negotiator2',
    version=version,
    packages=['negotiator2'],
    url='https://github.com/zimeon/negotiator2',
    author='Richard Jones and Simeon Warner',
    author_email='simeon.warner@cornell.edu',
    description="""Framework neutral HTTP Content Negotiation for Python""",
    license='CC0',
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    install_requires=[
        'datetime',
        'python-dateutil>=1.5'
    ],
    test_suite="tests",
    tests_require=[],
)
