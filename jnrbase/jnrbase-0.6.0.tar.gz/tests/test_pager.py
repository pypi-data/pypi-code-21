#
"""test_pager - Test pager piping support"""
# Copyright © 2014-2017  James Rowe <jnrowe@gmail.com>
#
# This file is part of jnrbase.
#
# jnrbase is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# jnrbase is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# jnrbase.  If not, see <http://www.gnu.org/licenses/>.

from os import getenv
from shutil import which

from pytest import mark

from jnrbase.pager import pager


@mark.skipif(not which('cat'), reason='Requires cat')
def test_pager(monkeypatch, capfd):
    pager('paging through cat', pager='cat')
    assert capfd.readouterr()[0] == 'paging through cat'


@mark.skipif(not which('less'), reason='Requires less')
def test_default_less_config(monkeypatch):
    monkeypatch.setattr('os.environ', {})
    pager('pager forcibly disabled')
    assert getenv('LESS') == 'FRSX'


def test_disable_pager(capsys):
    pager('pager forcibly disabled', pager=None)
    assert capsys.readouterr()[0] == 'pager forcibly disabled\n'
