# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import nose.tools as nt

from fastr import exceptions
from fastr.core.version import Version


class TestVersion():
    def setup(self):
        # Test different constructor
        self.data1 = Version()
        self.data2 = Version(0, 0, None, 'b', 42)
        self.data3 = Version((1, 2))
        self.data4 = Version([3, 4, [5, 6], 'beta', 3, None, '-'])
        self.data5 = Version('0.1-r3')
        self.data6 = Version('1.2.3.4.5.6.7-beta8_with_suffix')
        self.data7 = Version([3, 4, (5, 6), 'beta', 3, None, '-'])
        self.data8 = Version(u'3.3.2')

    def teardown(self):
        pass

    @nt.with_setup(setup, teardown)
    def test_data(self):
        nt.eq_(self.data1, (0, 0, None, None, None, None, None))
        nt.eq_(self.data2, (0, 0, None, 'b', 42, None, None))
        nt.eq_(self.data3, (1, 2, None, None, None, None, None))
        nt.eq_(self.data4, (3, 4, (5, 6), 'beta', 3, None, '-'))
        nt.eq_(self.data5, (0, 1, None, 're', 3, '', '-'))
        nt.eq_(self.data6, (1, 2, (3, 4, 5, 6, 7), 'beta', 8, '_with_suffix', '-'))
        nt.eq_(self.data7, (3, 4, (5, 6), 'beta', 3, None, '-'))
        nt.eq_(self.data8, (3, 3, (2,), None, None, '', None))

    @nt.with_setup(setup, teardown)
    def test_string(self):
        nt.eq_(str(self.data1), '0.0')
        nt.eq_(str(self.data2), '0.0b42')
        nt.eq_(str(self.data3), '1.2')
        nt.eq_(str(self.data4), '3.4.5.6-beta3')
        nt.eq_(str(self.data5), '0.1-r3')
        nt.eq_(str(self.data6), '1.2.3.4.5.6.7-beta8_with_suffix')
        nt.eq_(str(self.data7), '3.4.5.6-beta3')
        nt.eq_(str(self.data8), '3.3.2')

    @nt.with_setup(setup, teardown)
    def test_major(self):
        nt.eq_(self.data1.major, 0)
        nt.eq_(self.data2.major, 0)
        nt.eq_(self.data3.major, 1)
        nt.eq_(self.data4.major, 3)
        nt.eq_(self.data5.major, 0)
        nt.eq_(self.data6.major, 1)
        nt.eq_(self.data7.major, 3)
        nt.eq_(self.data8.major, 3)

    @nt.with_setup(setup, teardown)
    def test_minor(self):
        nt.eq_(self.data1.minor, 0)
        nt.eq_(self.data2.minor, 0)
        nt.eq_(self.data3.minor, 2)
        nt.eq_(self.data4.minor, 4)
        nt.eq_(self.data5.minor, 1)
        nt.eq_(self.data6.minor, 2)
        nt.eq_(self.data7.minor, 4)
        nt.eq_(self.data8.minor, 3)

    @nt.with_setup(setup, teardown)
    def test_extra(self):
        nt.eq_(self.data1.extra, None)
        nt.eq_(self.data2.extra, None)
        nt.eq_(self.data3.extra, None)
        nt.eq_(self.data4.extra, (5, 6))
        nt.eq_(self.data5.extra, None)
        nt.eq_(self.data6.extra, (3, 4, 5, 6, 7))
        nt.eq_(self.data7.extra, (5, 6))
        nt.eq_(self.data8.extra, (2,))

    @nt.with_setup(setup, teardown)
    def test_extra_string(self):
        nt.eq_(self.data1.extra_string, '')
        nt.eq_(self.data2.extra_string, '')
        nt.eq_(self.data3.extra_string, '')
        nt.eq_(self.data4.extra_string, '.5.6')
        nt.eq_(self.data5.extra_string, '')
        nt.eq_(self.data6.extra_string, '.3.4.5.6.7')
        nt.eq_(self.data7.extra_string, '.5.6')
        nt.eq_(self.data8.extra_string, '.2')

    @nt.raises(exceptions.FastrVersionInvalidError)
    def test_wrong_version_int(self):
        # Cannot use int, should raise an Error
        Version(2)

    @nt.raises(exceptions.FastrVersionInvalidError)
    def test_wrong_version_float(self):
        # Cannot use float, should raise an Error
        Version(3.0)

    @nt.raises(exceptions.FastrVersionInvalidError)
    def test_wrong_version_invalid_str(self):
        Version('test123')

    @nt.raises(exceptions.FastrVersionInvalidError)
    def test_wrong_version_list_too_long(self):
        Version(range(10))

