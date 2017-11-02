import os
import re
from distutils.core import setup

# about
__author__ = 'Justin Dane Vrana'
__license__ = 'MIT'
__package__ = "magicdir"
__readme__ = "README"
__version__ = "0.2.1a"

tests_require = [
    'pytest',
    'pytest-runner',
    'python-coveralls',
    'pytest-pep8'
]

install_requires = [
    'pathlib'
]

classifiers = [],

# setup functions
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# setup
setup(
        name=__package__,
        version=__version__,
        packages=[__package__],
        url='https://github.com/jvrana/magicdir',
        license=__license__,
        author=__author__,
        author_email='justin.vrana@gmail.com',
        keywords='directory python tree',
        description='intuitive python directory tree management for all',
        long_description=read(__readme__),
        install_requires=install_requires,
        python_requires='>=3.3',
        tests_require=tests_require,
)
