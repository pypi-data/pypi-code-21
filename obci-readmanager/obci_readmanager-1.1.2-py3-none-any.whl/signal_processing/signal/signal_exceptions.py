# -*- coding: utf-8 -*-
# Copyright (c) 2016-2018 Braintech Sp. z o.o. [Ltd.] <http://www.braintech.pl>
# All rights reserved.

"""Module provides classes for exceptions raised from DataProxy."""


class NoNextValue(Exception):
    """Raised when end of data file is met in self.get_next_value()."""


class NoNextTag(Exception):
    """Raised when end of tag file is met in self.get_next_tag()."""


class NoParameter(Exception):
    """Raised when there is a request for non-existing parameter in info file."""

    def __init__(self, p_param):
        """Initialize parameter."""
        self._param = p_param

    def __str__(self):
        """Return Exception message."""
        return "No parameter '{}' was found in info source!".format(self._param)


class BadSampleFormat(Exception):
    """
    An exception that should be raised when data sample has arrived and it is not float.

    Struct is unable to pack it.
    """

    def __str__(self):
        """Return Exception message."""
        return "Error! Received data sample is not of 'float' type! Writing to file aborted!"
