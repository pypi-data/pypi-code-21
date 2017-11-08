import re
import sys
PY25 = sys.version_info[0] == 2 and sys.version_info[1] <= 5

if PY25:
    from tools import ez_setup_py25 as ez_setup
else:
    from tools import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

__version__ = ''
__author__ = ''

f = open('src/batchcompute/__init__.py', 'r')
data = f.read()
__version__ = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        data, re.MULTILINE).group(1)
__author__ = re.search(r'^__author__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        data, re.MULTILINE).group(1)
f.close()

if not __version__:
    raise RuntimeError('Cannot find version information')

if not __author__:
    raise RuntimeError('Cannot find author information')

if PY25:
    dependencies = ['simplejson>=3.7.3', ]
else:
    dependencies = []

setup(
    name = 'batchcompute',
    version = __version__,
    description = 'Python SDK for aliyun batchcompute service',
    author = __author__,
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    zip_safe = False,
    license = 'GPL v2.0',
    install_requires = dependencies
)
