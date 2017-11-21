# Copyright (C) 2015 Red Hat
#
# This file is part of fedfind.
#
# fedfind is free software; you can redistribute it and/or modify
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Adam Williamson <awilliam@redhat.com>

"""Defines custom exceptions used by fedfind."""

from __future__ import unicode_literals
from __future__ import print_function

class FedfindError(Exception):
    """Base class for all fedfind errors."""
    pass

class PreviousRC1Error(FedfindError):
    """Special exception for trying to get previous_release of a TC1
    or RC1. Makes it easy to spot this case."""
    pass

class WaitError(FedfindError):
    """Error raised when some kind of wait has gone on too long."""
    pass

class DiscoveryError(FedfindError):
    """Raised when some kind of discovery attempt failed."""
    pass

# vim: set textwidth=100 ts=8 et sw=4:
