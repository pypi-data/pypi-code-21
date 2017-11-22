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
import copy
from typing import List, Sequence, Iterable

from hgicommon.data_source.common import DataSource, DataSourceType


class MultiDataSource(DataSource[DataSourceType]):
    """
    Aggregator of instances of data from multiple sources.
    """
    def __init__(self, sources: Iterable[DataSource]=()):
        """
        Constructor.
        :param sources: the sources of instances of `DataSourceType`
        """
        self.sources = copy.copy(sources)

    def get_all(self) -> Sequence[DataSourceType]:
        aggregated = []
        for source in self.sources:
            aggregated.extend(source.get_all())
        return aggregated


class ListDataSource(DataSource[DataSourceType]):
    """
    Data source where data is stored in a (changeable) list.
    """
    def __init__(self, data: List[DataSourceType]=None):
        if data is None:
            data = []
        self.data = data

    def get_all(self) -> Sequence[DataSourceType]:
        return self.data
