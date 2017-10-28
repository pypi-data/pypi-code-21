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

import os

# python 2 and python 3 compatibility
try:
    # python 3
    raw_input = raw_input
except:
    # python 3
    raw_input = input


def load_template(filename):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', filename), 'r') as file:
        return file.read()


def load_templates_folder(path):
    result = {}

    fullpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', path)

    for file in os.listdir(fullpath):
        result[file] = load_template(os.path.join(fullpath, file))

    return result


def raw_input_validated(question, default, valid, errormessage, validlistmessage=''):
    ask = True
    while ask:
        response = raw_input(question) or default
        if not response in valid:
            if '{}' in errormessage:
                print(errormessage.format(license))
            else:
                print(errormessage)

            if not validlistmessage == '':
                print(validlistmessage)
                print(', '.join(valid))
        else:
            ask = False

    return response
