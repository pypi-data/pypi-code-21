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
from typing import Iterable

from hgicommon.data_source.common import DataSourceType
from hgicommon.data_source.dynamic_from_file import RegisteringDataSource
from hgicommon.data_source.static_from_file import FilesDataSource, SynchronisedFilesDataSource
from hgicommon.models import Model


class StubModel(Model):
    """
    Stub `Model`.
    """
    def __init__(self):
        super(Model, self).__init__()


class StubFilesDataSource(FilesDataSource):
    """
    Stub `FilesDataSource`.
    """
    def is_data_file(self, file_path: str) -> bool:
        pass

    def extract_data_from_file(self, file_path: str) -> Iterable[DataSourceType]:
        pass


class StubSynchronisedInFileDataSource(SynchronisedFilesDataSource):
    """
    Stub `SynchronisedFilesDataSource`.
    """
    def is_data_file(self, file_path: str) -> bool:
        pass

    def extract_data_from_file(self, file_path: str) -> Iterable[DataSourceType]:
        pass


class StubRegisteringDataSource(RegisteringDataSource):
    """
    Stub implementation of `RegisteringDataSource`.
    """
    def is_data_file(self, file_path: str) -> bool:
        pass
