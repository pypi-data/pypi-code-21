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

import sympy

from fastr.core.dimension import HasDimensions, Dimension, ForwardsDimensions
from fastr import exceptions


class Dimensional(HasDimensions):
    """
    Test implementation of a HasDimensions class for testing.
    """
    SIZE = (42, 1337, sympy.Symbol('X'))
    NAME = ('answer', u'l33t', 'vague')

    def __init__(self):
        self._dimensions = tuple(Dimension(x, y) for x, y in zip(self.NAME, self.SIZE))

    @property
    def dimensions(self):
        return self._dimensions


class DimensionalForwarder(ForwardsDimensions):
    """
    Test the implementation of a ForwardsDimensions class
    """
    def __init__(self, source):
        self._source = source

    @property
    def source(self):
        return self._source

    def combine_dimensions(self, dimensions):
        """
        Strip out last dimension

        :param tuple dimensions: original dimensions
        :return: modified dimensions
        """
        return dimensions[:-1]


class TestDimension():
    """
    Test for the Dimension
    """
    def setup(self):
        self.cleese = Dimension('john', 196)
        self.cleese2 = Dimension('john', 196)
        self.palin = Dimension('michael', 178)
        self.dummy1 = Dimension('john', 42)
        self.dummy2 = Dimension('dummy', 196)
        self.jones = Dimension('terry', sympy.Symbol('length_jones'))

    def test_repr(self):
        nt.eq_(repr(self.cleese), '<Dimension john (196)>')
        nt.eq_(repr(self.palin), '<Dimension michael (178)>')

    def test_equal(self):
        nt.eq_(self.cleese, self.cleese2)
        nt.ok_(self.cleese != self.palin)
        nt.ok_(self.jones != self.palin)

        # Make sure not equal functions
        nt.eq_(self.cleese != self.cleese2, False)

        # Make sure partial correct dimensions do not match
        nt.ok_(self.cleese != self.dummy1)
        nt.ok_(self.cleese != self.dummy2)

    def test_name(self):
        nt.eq_(self.cleese.name, 'john')
        nt.eq_(self.palin.name, 'michael')
        nt.eq_(self.jones.name, 'terry')

    def test_size(self):
        nt.eq_(self.cleese.size, 196)
        nt.eq_(self.palin.size, 178)
        nt.eq_(self.jones.size, sympy.Symbol('length_jones'))

    def test_update(self):
        self.cleese.update_size(178)
        nt.eq_(self.cleese.size, 196)

        self.palin.update_size(196)
        nt.eq_(self.palin.size, 196)

        self.jones.update_size(sympy.Symbol('length_jones'))
        nt.eq_(self.jones.size, sympy.Symbol('length_jones'))

        self.jones.update_size(173)
        nt.eq_(self.jones.size, 173)

    @nt.raises(exceptions.FastrTypeError)
    def test_wrong_size_type_str(self):
        Dimension('eric', 'idle')

    @nt.raises(exceptions.FastrTypeError)
    def test_wrong_size_type_float(self):
        Dimension('graham', 1.88)

    @nt.raises(exceptions.FastrTypeError)
    def test_wrong_name_type_unicode(self):
        Dimension(u'terry\U0001F600', 173)

    @nt.raises(exceptions.FastrValueError)
    def test_wrong_value_size(self):
        Dimension('negative', -1)

    @nt.raises(exceptions.FastrTypeError)
    def test_wrong_update_type(self):
        self.cleese.update_size(1.96)

    @nt.raises(exceptions.FastrValueError)
    def test_wrong_update_value(self):
        self.jones.update_size(-173)


class TestHasDimension():
    """
    Tests for the Dimenions and HasDimensions mixin
    """
    def setup(self):
        self.test_object = Dimensional()

    def test_size(self):
        nt.eq_(self.test_object.size, self.test_object.SIZE)

    def test_dimnames(self):
        nt.eq_(self.test_object.dimnames, self.test_object.NAME)

    def test_ndims(self):
        nt.eq_(self.test_object.ndims, 3)


class TestForwardDimensions():
    """
    Test for the ForwardDimensions mixin
    """
    def setup(self):
        self.test_source = Dimensional()
        self.test_object = DimensionalForwarder(self.test_source)

    def test_size(self):
        nt.eq_(self.test_object.size, self.test_source.SIZE[:-1])

    def test_dimnames(self):
        nt.eq_(self.test_object.dimnames, self.test_source.NAME[:-1])

    def test_ndims(self):
        nt.eq_(self.test_object.ndims, 2)
