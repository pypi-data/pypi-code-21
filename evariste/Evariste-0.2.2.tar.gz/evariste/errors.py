# Copyright Louis Paternault 2015
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Errors and exceptions"""

class EvaristeError(Exception):
    """Generic error for evariste"""

    def __init__(self, msg=""):
        super().__init__()
        self.msg = msg

    def __str__(self):
        return self.msg

class EvaristeBug(Exception):
    """Bug: end-users should not see this."""
    def __init__(self, msg=""):
        super().__init__()
        self.msg = msg

    def __str__(self):
        return self.msg
