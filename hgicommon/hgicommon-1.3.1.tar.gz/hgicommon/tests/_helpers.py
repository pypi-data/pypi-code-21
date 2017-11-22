"""
Legalese
--------
Copyright (c) 2015 Genome Research Ltd.

Author: Colin Nolan <cn13@sanger.ac.uk>

This file is part of HGI's common Python library

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation; either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
import os
from tempfile import mkdtemp, mkstemp
from typing import Any, List, Callable

from math import ceil


def write_data_to_files_in_temp_directory(data: List[Any], spread_over_n_files: int, separator: str='\n', dir: str=None,
                                          file_prefix="") -> str:
    """
    Writes the given data over the given number of files in a temporary directory.
    :param data: the data that is to be written to the files
    :param spread_over_n_files: the number of files in which the data is to be spread over
    :param separator: the separator between data items in each file
    :param dir: the specific temp directory to use
    :param file_prefix: prefix to the files created
    :return: the location of the temp directory
    """
    if dir is None:
        dir = mkdtemp(suffix=write_data_to_files_in_temp_directory.__name__)

    datum_per_file = ceil(len(data) / spread_over_n_files)
    for i in range(spread_over_n_files):
        start_at = i * datum_per_file
        end_at = start_at + datum_per_file
        to_write = separator.join([str(x) for x in data[start_at:end_at]])

        write_to_temp_file(dir, to_write, file_prefix=file_prefix)

    return dir


def write_to_temp_file(dir: str, contents: str, file_prefix="") -> str:
    """
    Writes the given contents to a temp file, with the given name prefix, within the given directory.
    :param dir: the directory to place the temp file in
    :param contents: the contents of the temp file
    :param file_prefix: (optional) name prefix of the temp file
    :return: the path to the created temp file
    """
    temp_temp_file_location = mkstemp(dir=dir, prefix=file_prefix)[1]
    destination = os.path.join(dir, os.path.basename(temp_temp_file_location))

    with open(temp_temp_file_location, 'w') as file:
        file.write(contents)

    os.rename(temp_temp_file_location, destination)

    return destination


def extract_data_from_file(file_location: str, parser: Callable[[str], Any]=lambda data: data, separator: str=None) \
        -> List[Any]:
    """
    Extracts data from the file at the given location, using the given parser.
    :param file_location: the location of the file to read data from
    :param parser: the parser to extract data from the file
    :param separator: (optional) separator for data in the file
    :return: the extracted data
    """
    with open(file_location, 'r') as file:
        contents = file.read()

    if separator is not None:
        raw_data = contents.split(separator)
    else:
        raw_data = [contents]

    extracted = []
    for item in raw_data:
        parsed = parser(item)
        extracted.append(parsed)

    return extracted
