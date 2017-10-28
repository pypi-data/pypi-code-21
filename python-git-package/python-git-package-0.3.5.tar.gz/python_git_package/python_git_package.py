#!/usr/bin/env/ python
################################################################################
#    Copyright 2016 Brecht Baeten
#    This file is part of python-git-package.
#
#    python-git-package is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    python-git-package is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with python-git-package.  If not, see <http://www.gnu.org/licenses/>.
################################################################################

import sys
import os
import datetime
import re
import subprocess
import zipfile
import sphinx
import distutils.core

from . import utils

setup_file = utils.load_template('setup.py')
readme_file = utils.load_template('README.rst')
gitignore_file = utils.load_template('gitignore')
test_file = utils.load_template('tests.py')
function_scaffold = utils.load_template('function_scaffold.py')

license_headers = utils.load_templates_folder('license/header')
license_texts = utils.load_templates_folder('license/text')

docs_conf_file = utils.load_template('sphinx/conf.py')
docs_index_file = utils.load_template('sphinx/index.rst')
docs_packagename_file = utils.load_template('sphinx/packagename.rst')

thisfilepath = os.path.dirname(os.path.realpath(__file__))

def init():
    """
    Scaffolding

    Examples
    --------
    .. code-block:: bash

        pgp init

    """

    # default package data
    package_data = {}
    package_data['packagename'] = os.path.split(os.getcwd())[-1]
    package_data['description'] = ''
    package_data['url'] = ''
    package_data['author'] = 'me'
    package_data['author_email'] = ''
    package_data['license'] = 'MIT'
    package_data['python_version'] = '2.7'

    # current year
    now = datetime.datetime.now()
    package_data['year'] = now.year

    # check for existing files
    createsetup = True
    if os.path.isfile('setup.py'):
        response = utils.raw_input_validated(
            'A setup.py file was found, keep this file? (y)', 'y',
            ['y', 'n', 'yes', 'no'],
            'Error: {} is not a valid response',
            'Valid responses are:')
        if response in ['y', 'yes']:
            createsetup = False

    createmanifest = True
    if os.path.isfile('manifest.in'):
        response = utils.raw_input_validated(
            'A manifest.in file was found, keep this file? (y)', 'y',
            ['y', 'n', 'yes', 'no'],
            'Error: {} is not a valid response',
            'Valid responses are:')
        if response in ['y', 'yes']:
            createmanifest = False

    createlicense = True
    if os.path.isfile('LICENSE') or os.path.isfile('license') or os.path.isfile('LICENSE.txt') or os.path.isfile(
            'license.txt') or os.path.isfile('LICENSE.md') or os.path.isfile('license.md'):
        response = utils.raw_input_validated(
            'A license file was found, keep this file? (y)', 'y',
            ['y', 'n', 'yes', 'no'],
            'Error: {} is not a valid response',
            'Valid responses are:')
        if response in ['y', 'yes']:
            createlicense = False

    createreadme = True
    if os.path.isfile('README') or os.path.isfile('readme') or os.path.isfile('README.rst') or os.path.isfile(
            'readme.rst') or os.path.isfile('README.md') or os.path.isfile('readme.md'):
        response = utils.raw_input_validated(
            'A readme file was found, keep this file? (y)', 'y',
            ['y', 'n', 'yes', 'no'],
            'Error: {} is not a valid response',
            'Valid responses are:')
        if response in ['y', 'yes']:
            createreadme = False

    creategitignore = True
    if os.path.isfile('.gitignore'):
        response = utils.raw_input_validated(
            'A .gitignore file was found, keep this file? (y)', 'y',
            ['y', 'n', 'yes', 'no'],
            'Error: {} is not a valid response',
            'Valid responses are:')
        if response in ['y', 'yes']:
            creategitignore = False

    createdocs = True
    if os.path.isdir('doc'):
        response = utils.raw_input_validated(
            'A doc directory was found, keep this directory? (y)', 'y',
            ['y', 'n', 'yes', 'no'],
            'Error: {} is not a valid response',
            'Valid responses are:')
        if response in ['y', 'yes']:
            createdocs = False
    else:
        response = utils.raw_input_validated(
            'Create sphinx doc directory? (y)', 'y',
            ['y', 'n', 'yes', 'no'],
            'Error: {} is not a valid response',
            'Valid responses are:')
        if response in ['n', 'no']:
            createdocs = False

    # check existing files for package data
    if not createsetup:
        package_data.update(get_data_from_setup())

    # ask for the package data
    print('')
    package_data['packagename'] = utils.raw_input('Package name ({}): '.format(package_data['packagename']))\
        or package_data['packagename']
    package_data['packagename_file'] = package_data['packagename'].replace('-', '_')
    package_data['packagename_caps'] = package_data['packagename_file'].title()
    package_data['packagename_underline'] = package_data['packagename'] + '\n' + '=' * len(package_data['packagename'])
    package_data['description'] = utils.raw_input('Package description ({}): '.format(package_data['description'])) \
        or package_data['description']
    package_data['url'] = utils.raw_input('Package url ({}): '.format(package_data['url'])) or package_data['url']
    package_data['author'] = utils.raw_input('Author ({}): '.format(package_data['author'])) or package_data['author']
    package_data['author_email'] = utils.raw_input('Author email ({}): '.format(package_data['author_email'])) \
        or package_data['author_email']
    package_data['license'] = utils.raw_input_validated(
        'License ({}): '.format(package_data['license']),
        package_data['license'],
        license_texts.keys(),
        'Error: {} is not a valid license name',
        'Valid licence names are:')
    package_data['python_version'] = utils.raw_input('Python version ({}): '.format(package_data['python_version'])) \
        or package_data['python_version']

    # create folders
    if not os.path.exists(package_data['packagename_file']):
        os.makedirs(package_data['packagename_file'])
    if not os.path.exists('tests'):
        os.makedirs('tests')
    if not os.path.exists('examples'):
        os.makedirs('examples')

    # create files if they are not present
    if createsetup:
        file = open('setup.py', 'w+')
        file.write(setup_file.format(**package_data))
        file.close()

    if createmanifest:
        file = open('manifest.in', 'w+')
        file.write('include README.md\ninclude LICENSE\ninclude examples/example.py')
        file.close()

    if createreadme:
        file = open('README.rst', 'w+')
        file.write(readme_file.format(**package_data))
        file.close()

    if createlicense:
        file = open('LICENSE', 'w+')
        file.write(license_texts[package_data['license']])
        file.close()

    if creategitignore:
        file = open('.gitignore', 'w+')
        file.write(gitignore_file)
        file.close()

    if createdocs:
        if not os.path.isdir('doc'):
            os.mkdir('doc')
        if not os.path.isdir('doc/source'):
            os.mkdir('doc/source')
        if not os.path.isdir('doc/build'):
            os.mkdir('doc/build')
        if not os.path.isdir('doc/source/_static'):
            os.mkdir('doc/source/_static')
        if not os.path.isdir('doc/source/_templates'):
            os.mkdir('doc/source/_templates')

        file = open('doc/source/conf.py', 'w+')
        file.write(docs_conf_file.format(**package_data))
        file.close()

        file = open('doc/source/index.rst', 'w+')
        file.write(docs_index_file.format(**package_data))
        file.close()

        file = open('doc/source/{}.rst'.format(package_data['packagename_file']), 'w+')
        file.write(docs_packagename_file.format(**package_data))
        file.close()

        file = open('doc/.gitignore', 'w+')
        file.write('build')
        file.close()

    filename = os.path.join(package_data['packagename_file'], '__init__.py')
    if not os.path.isfile(filename):
        file = open(filename, 'w+')
        file.write('from .__version__ import version as __version__\n')
        file.write('from {} import *\n'.format(package_data['packagename_file']))
        file.close()

    filename = os.path.join(package_data['packagename_file'], '__version__.py')
    if not os.path.isfile(filename):
        file = open(filename, 'w+')
        file.write('version = \'0.0.0\'')
        file.close()

    filename = os.path.join(package_data['packagename_file'], '{}.py'.format(package_data['packagename_file']))
    if not os.path.isfile(filename):
        file = open(filename, 'w+')
        file.write(license_headers[package_data['license']].format(**package_data))
        file.write('\n')
        file.write(function_scaffold)
        file.close()

    filename = os.path.join('examples', 'example.py')
    if not os.path.isfile(filename):
        file = open(filename, 'w+')
        file.write(license_headers[package_data['license']].format(**package_data))
        file.close()

    filename = os.path.join('tests', 'test_{}.py'.format(package_data['packagename_file']))
    if not os.path.isfile(filename):
        file = open(filename, 'w+')
        file.write(license_headers[package_data['license']].format(**package_data))
        file.write(test_file.format(**package_data))
        file.close()

    filename = os.path.join('tests', 'all.py')
    if not os.path.isfile(filename):
        file = open(filename, 'w+')
        file.write(license_headers[package_data['license']].format(**package_data))
        file.write('import unittest\n\n')
        file.write('from test_{packagename_file} import *\n\n'.format(**package_data))
        file.write('if __name__ == \'__main__\':\n    unittest.main()')
        file.close()

    # initialise a git repository
    subprocess.check_output(['git', 'init'])[:-1]
    subprocess.check_output(['git', 'add', '.'])[:-1]
    subprocess.check_output(['git', 'commit', '-m', 'initial commit'])[:-1]
    subprocess.check_output(['git', 'checkout', '-b', 'dev'])


def release():
    """
    Creates a new release
    
    Examples
    --------
    .. code-block:: bash
    
        pgp release
        
    """

    # search for a version file
    versionfilename = ''
    for d in os.walk('.'):
        if not 'build' in d[0] and not 'lib' in d[0]:
            filename = os.path.join(d[0], '__version__.py')
            if os.path.isfile(filename):
                versionfilename = filename
                break

    if filename == '':
        print('Could not find __version__.py')
        # get the previous version number from git
        output = subprocess.check_output(['git', 'tag'])[:-1]
        if isinstance(output, bytes):
            output = output.decode('utf-8')

        if not output == '':
            splitoutput = output.split('\n')
            oldversion = splitoutput[-1]

    else:
        # try to get the old version number from __version__.py
        try:
            with open(versionfilename, 'r') as f:
                content = f.readline()
                splitcontent = content.split('\'')
                oldversion = splitcontent[1]
        except:
            print('Error while checking the version number. Check __version__.py')
            return

    splitoldversion = oldversion.split('.')

    print('previous version: {}'.format(oldversion))

    # ask for a new version number
    version_ok = False
    while not version_ok:
        version = utils.raw_input('new version number: ')
        try:
            # check if the new version is higher than the old version
            splitversion = version.split('.')

            splitversion += [0]*(len(splitoldversion)-len(splitversion))
            splitoldversion += [0]*(len(splitversion)-len(splitoldversion))
            if sum([int(v) * 1000 ** i for i, v in enumerate(splitversion[::-1])]) <= sum(
                    [int(v) * 1000 ** i for i, v in enumerate(splitoldversion[::-1])]):
                print('The new version ({}) is not higher than the old version ({})'.format(version, oldversion))
            else:
                version_ok = True
        except:
            print('Invalid version')

    branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])[:-1]

    # changelog = ''
    # response = utils.raw_input_validated(
    #     'Did you update the changelog? ', '',
    #     ['y', 'n', 'yes', 'no'],
    #     'Error: {} is not a valid response',
    #     'Valid responses are:')
    # if response in ['n', 'no']:
    #     print('Update the changelog before issuing a release')
    #     return

    print('')
    print('GIT branch: {}'.format(branch))
    print('Version: {}'.format(version))

    response = utils.raw_input_validated(
        'Is this ok? ', '',
        ['y', 'n', 'yes', 'no'],
        'Error: {} is not a valid response',
        'Valid responses are:')
    if response in ['n', 'no']:
        print('Exit')
        return

    # write the new version number to version.py
    with open(versionfilename, 'w') as f:
        f.write('version = \'{}\''.format(version))

    # build the documentation
    if os.path.exists('doc/source'):
        doc()

    # create a commit message
    message = 'Created new version\nVersion: {}'.format(version)
    message += '\nThis is an automated commit.'

    # create the commit
    output = subprocess.check_output(['git', 'commit', '-a', '-m', message])[:-1]

    # merge the branch with master
    output = subprocess.check_output(['git', 'checkout', 'master'])[:-1]
    output = subprocess.check_output(['git', 'merge', branch])[:-1]

    # add a git tag
    output = subprocess.check_output(['git', 'tag', '{}'.format(version)])[:-1]

    # checkout the old branch
    output = subprocess.check_output(['git', 'checkout', branch])[:-1]

    # build an sdist
    distutils.core.run_setup('setup.py', script_args=['sdist'])


def doc():
    """
    Builds the documentation to html using Sphinx

    Examples
    --------
    .. code-block:: bash

        pgp doc

    """

    # check if the doc folder exists
    sourcedir = os.path.join('doc', 'source')
    builddir = os.path.join('doc', 'build', 'html')

    if os.path.exists(sourcedir):
        output = sphinx.main(['html', sourcedir, builddir])
        print(output)

        # create a zip file
        zipf = zipfile.ZipFile(os.path.join(builddir, 'html.zip'), 'w', zipfile.ZIP_DEFLATED)
        for root, dirs, files in os.walk(os.path.join(builddir, 'html')):

            for file in files:
                fname = os.path.join(root, file)
                aname = os.path.relpath(os.path.join(root, file), os.path.join(builddir, 'html'))
                zipf.write(fname, aname)
                # zipf.write(os.path.join(root, file))

        zipf.close()

    else:
        print('Error: no sphinx documentation source found.')
        print('Check doc/source')


def get_data_from_setup():
    package_data = {}

    with open('setup.py', 'r') as f:
        for line in f:

            match_obj = re.match('.*name=\'(.*)\'', line)
            if match_obj:
                package_data['name'] = match_obj.group(1)

            match_obj = re.match('.*description=\'(.*)\'', line)
            if match_obj:
                package_data['description'] = match_obj.group(1)

            match_obj = re.match('.*author=\'(.*)\'', line)
            if match_obj:
                package_data['author'] = match_obj.group(1)

            match_obj = re.match('.*author_email=\'(.*)\'', line)
            if match_obj:
                package_data['author_email'] = match_obj.group(1)

            match_obj = re.match('.*url=\'(.*)\'', line)
            if match_obj:
                package_data['url'] = match_obj.group(1)

            match_obj = re.match('.*license=\'(.*)\'', line)
            if match_obj:
                package_data['license'] = match_obj.group(1)

    return package_data


def execute_from_command_line():
    command = sys.argv[1]

    if command == 'init':
        init()

    elif command == 'release':
        release()

    elif command == 'doc':
        doc()

    else:
        print('not a valid command')
        print('usage:')
