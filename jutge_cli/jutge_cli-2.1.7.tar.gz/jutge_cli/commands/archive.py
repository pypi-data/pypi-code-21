#!/usr/bin/python3

# Copyright (C) 2017  Aleix Boné (abone9999 at gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Provide the function `archive` to move a file to the archive folder

This should be used to save a local copy of accepted problems from jutge.org
"""

from logging import getLogger
from os import makedirs, symlink, remove
from os.path import isdir, isfile, basename
from shutil import move, copyfile

LOG = getLogger('jutge.archive')


def archive(prog: "FileType('w')", code: str, title: str, folder: str,
        problem_sets: 'Boolean' = None, overwrite: 'Boolean' = False,
        copy: 'Boolean' = False, **kwargs):
    """Move file to the archive

    :param prog: program file to archive
    :param title: program title to use when archiving file
    :param folder: archive folder
    :param problem_sets: problem_sets to consider
    :param overwrite: if True, overwrite program file if already in database
    :param copy: if True, copy program instead of moving it
    """

    ext = basename(prog.name).split('.')[-1]

    sym_link = None

    sub_code = code.split('_')[0]

    if problem_sets is not None:
        for sub_folder, problems in problem_sets.items():
            if sub_code in problems:
                sym_link = '{}/{}'.format(folder, sub_folder)
                if not isdir(sym_link):
                    makedirs(sym_link)

    destination = '{}/{}.{}'.format(folder, title, ext)
    if not isfile(destination) or overwrite:
        if not copy:
            move(prog.name, destination)
        else:
            copyfile(prog.name, destination)
    else:
        LOG.error('File already in DB')

    if sym_link is not None:
        sym_link = '{}/{}.{}'.format(sym_link, title, ext)
        try:
            symlink(destination, sym_link)
            LOG.debug('Symlink %s -> %s', sym_link, destination)
            if isfile(prog.name) and not copy:
                remove(prog.name)
        except FileExistsError:
            LOG.error('Symlink already exists')

    LOG.debug(destination)
