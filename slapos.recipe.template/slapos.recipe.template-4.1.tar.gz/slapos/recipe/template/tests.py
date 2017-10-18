##############################################################################
#
# Copyright (c) 2010-2012 Vifib SARL and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
from __future__ import print_function
import doctest
import unittest
from zc.buildout import testing
from zope.testing import renormalizing

def setUp(test):
  testing.buildoutSetUp(test)
  testing.install_develop('slapos.recipe.template', test)
  (lambda system, buildout, **kw: test.globs.update(
      run_buildout = lambda: print(system(buildout), end='')
      ))(**test.globs)

def test_suite():
  return unittest.TestSuite([
    doctest.DocFileSuite(
      filename,
      setUp=setUp,
      tearDown=testing.buildoutTearDown,
      checker=renormalizing.RENormalizing((
        testing.normalize_path,
        testing.not_found,
        )),
    ) for filename in [
      'README.txt',
      'README.jinja2.txt',
    ]
  ])

if __name__ == '__main__':
  unittest.main(defaultTest='test_suite')
