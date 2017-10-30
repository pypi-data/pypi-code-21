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

"""Provides function import_zip to import problems from zip file to database
"""

from glob import glob
from logging import getLogger
from os import makedirs, symlink
from os.path import basename, isdir
from shutil import copyfile
from tempfile import TemporaryDirectory
from time import sleep
from zipfile import ZipFile

from .show import get_title

LOG = getLogger('jutge.import_zip')


def import_zip(zip_file: str, folder: str, database: str,
        problem_sets: 'Boolean' = None, delay: int = 100,
        overwrite: 'Boolean' =False, **kwargs):
    """Import problems from zip file to archive

    The zip file must match the exact structure of the one that is downloaded
    from jutge.org profile page

    :param zip: zip file to import
    :param folder: archive folder to where files are imported
    :param overwrite: overwrite existing files in database
    :param problem_sets: problem sets to consider when importing
    :param delay: delay between jutge.org connections
    :param no_download: do not connect to jutge.org (save as code.ext)
    """

    extract_to = TemporaryDirectory().name

    with ZipFile(zip_file.name, 'r') as opened_zip_file:
        opened_zip_file.extractall(extract_to)

    if not isdir(folder):
        makedirs(folder)

    extensions = ['cc', 'c', 'hs', 'php', 'bf', 'py']

    count = 0

    for problem in glob(extract_to + '/*'):
        try:
            code = basename(problem)

            sources = []

            for ext in extensions:
                match = glob('{}/*AC.{}'.format(problem, ext))
                if match:
                    sources.append([match[-1], ext])    # take last AC

            for source in sources:
                ext = source[1]
                if ext == 'cc':
                    ext = 'cpp'     # Use cpp over cc for c++ files

                if overwrite or not glob(
                        '{}/{}*.{}'.format(folder, code, ext)):

                    name = get_title(code=code, database=database)

                    if name is None or name == 'Error':
                        name = code

                    file_name = '{}/{}.{}'.format(folder, name, ext)

                    copyfile(source[0], file_name)
                    LOG.info('Copied %a to %s ...', source[0], file_name)

                    sub_code = code.split('_')[0]
                    sym_link = '.'

                    if problem_sets is not None:
                        for sub_folder, problems in problem_sets.items():
                            if sub_code in problems:
                                sym_link = '{}/{}'.format(folder, sub_folder)
                                if not isdir(sym_link):
                                    makedirs(sym_link)

                    if sym_link != '.':
                        sym_link = '{}/{}.{}'.format(sym_link, name, ext)
                        try:
                            symlink(source, sym_link)
                            LOG.debug('Symlink %s -> %s', sym_link, source[0])
                        except FileExistsError:
                            LOG.warning('Symlink already exists')

                    count += 1

                    if delay > 0:
                        sleep(delay / 1000.0)

        except:
            LOG.warning('Skipping %s', folder)

    LOG.info('FINISHED; Added %d programs', count)
