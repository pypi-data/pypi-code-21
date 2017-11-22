"""
Legalese
--------
Copyright (c) 2015, 2016 Genome Research Ltd.

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
from time import sleep

from watchdog.events import FileSystemEventHandler, os

from hgicommon.data_source import SynchronisedFilesDataSource


def block_until_synchronised_files_data_source_started(source: SynchronisedFilesDataSource):
    """
    Blocks until the given synchronised files data source has started to notice changes in the file system (may be a few
    milliseconds after it has been started).
    :param source: the synchronised files data source that has been started
    """
    blocked = True

    def unblock(*args):
        nonlocal blocked
        blocked = False

    event_handler = FileSystemEventHandler()
    event_handler.on_modified = unblock
    source._observer.schedule(event_handler, source._directory_location, recursive=True)

    temp_file_name = ".temp_%s" % block_until_synchronised_files_data_source_started.__name__
    temp_file_path = os.path.join(source._directory_location, temp_file_name)
    i = 0
    while blocked:
        with open(temp_file_path, 'a') as file:
            file.write(str(i))
        sleep(10 / 1000)
        i += 1

    # XXX: Not removing the temp file to avoid the notification.
    # XXX: Not unscheduling as observer does not like it for some reason.
