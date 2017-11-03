import os
import sys
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    long_description = readme.read()

install_requires = ['setuptools_scm', 'nuitka', ]

PY2 = sys.version_info[0] == 2
if PY2:
    install_requires.append('pathlib2')


setup(
    name='nuitka_setuptools',
    py_modules=['nuitka_setuptools'],
    description='Extension to setuptools to run your package through nuitka to '
                'produce compiled, faster, obfuscated binary modules.',
    long_description=long_description,
    author='Andrew Leech',
    author_email='andrew@alelec.net',
    url='https://gitlab.com/alelec/nuitka-setuptools',
    use_scm_version=True,
    include_package_data=True,
    install_requires=install_requires,
    setup_requires=['setuptools_scm']
)
