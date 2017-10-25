# -*- coding: utf-8 -*-
# Copyright (c) 2016-2018 Braintech Sp. z o.o. [Ltd.] <http://www.braintech.pl>
# All rights reserved.

"""
This module provides classes for managing data from info source.

Author:
    Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
"""
import copy

from . import info_file_proxy
from . import signal_exceptions
from . import signal_logging as logger


LOGGER = logger.get_logger('read_info_source', 'info')


class InfoSource:
    """Base InfoSource class."""

    def get_param(self, p_key):
        """Method must be implemented in subclass."""
        LOGGER.error("The method must be subclassed")

    def get_params(self):
        """Method must be implemented in subclass."""
        LOGGER.error("The method must be subclassed")

    def set_params(self, p_params):
        """Method must be implemented in subclass."""
        LOGGER.error("The method must be subclassed")

    def update_params(self, p_params):
        """Method must be implemented in subclass."""
        LOGGER.error("The method must be subclassed")

    def set_param(self, k, v):
        """Method must be implemented in subclass."""
        LOGGER.error("The method must be subclassed")

    def reset_params(self):
        """Method must be implemented in subclass."""
        LOGGER.error("The method must be subclassed")

    def __deepcopy__(self, memo):
        """Construct a new object, next recursively, inserts copies into it of the :class MemoryInfoSource."""
        return MemoryInfoSource(copy.deepcopy(self.get_params()))


class MemoryInfoSource(InfoSource):
    """Subclass of class 'InfoSource', stores parameters in memory in 'dict' structure."""

    def __init__(self, p_params={}):
        """Initialize parameters as dictionary structure."""
        self._params = None
        self.set_params(p_params)

    def set_params(self, p_params):
        """Set parameters in 'dict' structure."""
        self._params = dict(p_params)

    def reset_params(self):
        """Reset parameters self.set_params({})-> empty 'dict'."""
        self.set_params({})

    def update_params(self, p_params):
        """Update parameters in 'dict' structure."""
        for k, v in p_params.items():
            self.set_param(k, v)

    def set_param(self, p_key, p_value):
        """Set parameter dict(p_key: p_value)."""
        self._params[p_key] = p_value

    def get_param(self, p_key):
        """For key, returns value or signal_exceptions.NoParameter if key not in dictionary."""
        try:
            return self._params[p_key]
        except KeyError:
            raise signal_exceptions.NoParameter(p_key)

    def get_params(self):
        """Return all params in 'dict' structure of keys and values."""
        return self._params


class FileInfoSource(InfoSource):
    """Subclass of class 'InfoSource', manage parameters from file and memory_source, parameters: 'dict'."""

    def __init__(self, p_file):
        """Initialize _info_proxy, read from p_file if there is no memory_source."""
        self._memory_source = None
        if isinstance(p_file, str):
            self._info_proxy = info_file_proxy.InfoFileReadProxy(p_file)
        else:
            self._info_proxy = p_file

    def get_param(self, p_key):
        """For key, if memory_source is None returns param from info_proxy, else returns param from _memory_source."""
        if self._memory_source is None:
            return self._info_proxy.get_param(p_key)
        else:
            return self._memory_source.get_param(p_key)

    def get_params(self):
        """If memory_source is None returns all_params from info_proxy, else returns all_params from _memory_source."""
        if self._memory_source is None:
            return self._info_proxy.get_params()
        else:
            return self._memory_source.get_params()

    def _get_memory_source(self):
        if self._memory_source is None:
            self._memory_source = MemoryInfoSource(self._info_proxy.get_params())
        return self._memory_source

    def set_param(self, k, v):
        """Set param (key and value0) in memory source."""
        self._get_memory_source().set_param(k, v)

    def set_params(self, p_params):
        """Set params in memory source."""
        self._get_memory_source().set_params(p_params)

    def update_params(self, p_params):
        """Update params in memory source."""
        self._get_memory_source().update_params(p_params)

    def reset_params(self):
        """Reset all params in memory source."""
        self._get_memory_source().reset_params()
