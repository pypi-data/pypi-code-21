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

"""Test of evariste compilation"""

import logging
import os
import shutil

import evariste
from evariste.setup import Setup
from evariste.utils import ChangeDir

from . import TestCompilation

LOGGER = logging.getLogger(evariste.__name__)

DATA = os.path.join(
    os.path.dirname(__file__),
    'test_misc_data',
    )

class TestRun(TestCompilation):
    """Testing setup `libdirs` options"""
    # pylint: disable=too-few-public-methods

    def test_misc(self):
        """Test a miscallaenous compilation (nothing specific here)."""
        with ChangeDir(DATA):
            shutil.rmtree("dest", ignore_errors=True)
            os.makedirs("dest", exist_ok=True)
            self._run_evariste(Setup.from_file("evariste.setup"))
            try:
                self.assertTreeEqual(
                    "expected",
                    "dest",
                    )
            except AssertionError:
                LOGGER.error(
                    "Temporary tree has been kept in {}.".format(
                        os.path.join(DATA, "dest")
                        )
                    )
                raise
