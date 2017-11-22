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
from typing import Generic, Sequence, TypeVar, Callable, Optional

_ListenableDataType = TypeVar("ListenableDataType")


class Listenable(Generic[_ListenableDataType]):
    """
    Class on which listeners can be added.
    """
    _NO_DATA_MARKER = object()

    def __init__(self):
        self._listeners = []

    def get_listeners(self) -> Sequence[Callable[[_ListenableDataType], None]]:
        """
        Get all of the registered listeners.
        :return: list of the registered listeners
        """
        return self._listeners

    def add_listener(self, listener: Callable[[_ListenableDataType], None]):
        """
        Adds a listener.
        :param listener: the event listener
        """
        self._listeners.append(listener)

    def remove_listener(self, listener: Callable[[_ListenableDataType], None]):
        """
        Removes a listener.
        :param listener: the event listener to remove
        """
        self._listeners.remove(listener)

    def notify_listeners(self, data: Optional[_ListenableDataType]=_NO_DATA_MARKER):
        """
        Notify event listeners, passing them the given data (if any).
        :param data: the data to pass to the event listeners
        """
        for listener in self._listeners:
            if data is not Listenable._NO_DATA_MARKER:
                listener(data)
            else:
                listener()
