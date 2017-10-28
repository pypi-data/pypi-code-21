#!/usr/bin/env/ python
from setuptools import setup
import os

# retrieve the version
try:
    versionfile = os.path.join('python_git_package', '__version__.py')
    f = open(versionfile, 'r')
    content = f.readline()
    splitcontent = content.split('\'')
    version = splitcontent[1]
    f.close()
except:
    raise Exception('Could not determine the version from python_git_package/__version__.py')

# run the setup command
setup(
    name='python-git-package',
    version=version,
    license='GPLv3',
    description='A scaffolding tool for python packages',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    url='https://github.com/BrechtBa/python-git-package',
    author='Brecht Baeten',
    author_email='brecht.baeten@gmail.com',
    packages=['python_git_package'],
    package_data={'python_git_package': [
        'templates/*',
        'templates/sphinx/*',
        'templates/license/header/*',
        'templates/license/text/*']},
    install_requires=['sphinx', 'sphinx_rtd_theme', 'numpydoc'],
    classifiers=['Programming Language :: Python :: 2.7'],
    entry_points={'console_scripts': [
        'python-git-package=python_git_package:execute_from_command_line',
        'pgp=python_git_package:execute_from_command_line',
    ]},
    data_files=[(root, [os.path.join(root, f) for f in files]) for root, subfolders, files in
                os.walk(os.path.join('python_git_package', 'templates'))]
)
