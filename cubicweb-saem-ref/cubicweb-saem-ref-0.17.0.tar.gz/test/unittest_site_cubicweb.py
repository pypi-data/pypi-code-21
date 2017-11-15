# copyright 2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-saem_ref unit tests for site_cubicweb"""

from datetime import datetime

import unittest

from cubicweb import devtools  # noqa

from cubicweb_saem_ref.site_cubicweb import print_tzdatetime_local


class PrintTZDatetimeTC(unittest.TestCase):

    def test(self):
        class req(object):
            @staticmethod
            def property_value(prop):
                return {'ui.timezone': 'Europe/Paris',
                        'ui.datetime-format': '%Y/%m/%d %H:%M'}[prop]
        value = datetime(2015, 5, 26, 14, 12)
        self.assertEqual(print_tzdatetime_local(value, req),
                         '2015/05/26 16:12')


if __name__ == '__main__':
    unittest.main()
