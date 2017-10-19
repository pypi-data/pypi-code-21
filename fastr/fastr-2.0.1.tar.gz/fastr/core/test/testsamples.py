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

import pickle
from collections import OrderedDict

import nose.tools as nt

import fastr
from fastr.core.samples import SampleId, SampleIndex, SampleItem
from fastr import exceptions

String = fastr.typelist['String']


class TestSamples():
    def setup(self):
        self.sample_id_0 = SampleId('single')
        self.sample_id_1 = SampleId('test', '123', 'test')
        self.sample_id_2 = SampleId(['built', 'from', 'list'])

        self.sampleindex_0 = SampleIndex(0)
        self.sampleindex_1 = SampleIndex(42, 4, 2)
        self.sampleindex_2 = SampleIndex([5, 3, 8])
        self.sampleindex_3 = SampleIndex(xrange(3))  # Create index from iterator
        self.sampleindex_4 = SampleIndex(0, slice(3, 5))
        self.sampleindex_5 = SampleIndex(slice(1, 6, 2), 3)
        self.sampleindex_6 = SampleIndex(slice(None, None, 2))
        self.sampleindex_7 = SampleIndex(slice(None, 9, 3))
        self.sampleindex_8 = SampleIndex(slice(None, 5, 2), slice(1, 4))

        self.sample_item_0 = SampleItem(self.sampleindex_0, self.sample_id_0, OrderedDict(), None)
        self.sample_item_1 = SampleItem(self.sampleindex_1, self.sample_id_1, OrderedDict({0: (String('val1'), String('val2'))}), set())
        self.sample_item_2 = SampleItem((0, 1), ('a', 'b'), OrderedDict({0: (String('val1'), String('val2'))}), set())

    def test_failed_sample_default(self):
        nt.eq_(self.sample_item_0.failed_annotations, set())

    def test_failed_sample_add_failure(self):
        sample_item = SampleItem(self.sampleindex_0, self.sample_id_0, OrderedDict(), None, set())
        sample_item.failed_annotations.add(('job_0', "because of what?"))
        nt.eq_(sample_item.failed_annotations, {('job_0', "because of what?")})

    def test_failed_sample_add_multiple_failures(self):
        sample_item = SampleItem(self.sampleindex_0, self.sample_id_0, OrderedDict(), None, set())
        sample_item.failed_annotations.add(('job_0', "because of what?"))
        sample_item.failed_annotations.add(('job_1', "because of that"))
        nt.eq_(sample_item.failed_annotations, {('job_0', "because of what?"), ('job_1', "because of that")})

    @nt.raises(exceptions.FastrTypeError)
    def test_failed_sample_add_wrong_type(self):
        sample_item = SampleItem((0, 1), ('a', 'b'), OrderedDict({0: (String('val1'), String('val2'))}), set(), "blaat")

    def test_sample_id_str(self):
        nt.eq_(str(self.sample_id_0), 'single')
        nt.eq_(str(self.sample_id_1), 'test__123__test')
        nt.eq_(str(self.sample_id_2), 'built__from__list')

    @nt.raises(exceptions.FastrTypeError)
    def test_sampleid_noniter(self):
        SampleId(None)

    @nt.raises(exceptions.FastrValueError)
    def test_sampleindex_empty(self):
        SampleIndex()

    @nt.raises(exceptions.FastrValueError)
    def test_sampleindex_emptylist(self):
        SampleIndex([])

    @nt.raises(exceptions.FastrTypeError)
    def test_sampleindex_noniter(self):
        SampleIndex(None)

    @nt.raises(exceptions.FastrTypeError)
    def test_sampleindex_wrongtype1(self):
        SampleIndex('test')

    @nt.raises(exceptions.FastrTypeError)
    def test_sampleindex_wrongtype2(self):
        SampleIndex(['test', 1, 2, 3])

    @nt.raises(exceptions.FastrTypeError)
    def test_sampleindex_wrongtype3(self):
        SampleIndex(1.0, 2.0)

    def test_sampleindex_str(self):
        nt.eq_(str(self.sampleindex_0), '(0)')
        nt.eq_(str(self.sampleindex_1), '(42, 4, 2)')
        nt.eq_(str(self.sampleindex_2), '(5, 3, 8)')
        nt.eq_(str(self.sampleindex_3), '(0, 1, 2)')
        nt.eq_(str(self.sampleindex_4), '(0, 3:5)')
        nt.eq_(str(self.sampleindex_5), '(1:6:2, 3)')
        nt.eq_(str(self.sampleindex_6), '(::2)')
        nt.eq_(str(self.sampleindex_7), '(:9:3)')
        nt.eq_(str(self.sampleindex_8), '(:5:2, 1:4)')

    def test_sampleindex_repr(self):
        nt.eq_(repr(self.sampleindex_0), '<SampleIndex (0)>')
        nt.eq_(repr(self.sampleindex_1), '<SampleIndex (42, 4, 2)>')
        nt.eq_(repr(self.sampleindex_2), '<SampleIndex (5, 3, 8)>')
        nt.eq_(repr(self.sampleindex_3), '<SampleIndex (0, 1, 2)>')
        nt.eq_(repr(self.sampleindex_4), '<SampleIndex (0, 3:5)>')
        nt.eq_(repr(self.sampleindex_5), '<SampleIndex (1:6:2, 3)>')
        nt.eq_(repr(self.sampleindex_6), '<SampleIndex (::2)>')
        nt.eq_(repr(self.sampleindex_7), '<SampleIndex (:9:3)>')
        nt.eq_(repr(self.sampleindex_8), '<SampleIndex (:5:2, 1:4)>')

    def test_sampleindex_isslice(self):
        nt.ok_(not self.sampleindex_0.isslice)
        nt.ok_(not self.sampleindex_1.isslice)
        nt.ok_(not self.sampleindex_2.isslice)
        nt.ok_(not self.sampleindex_3.isslice)
        nt.ok_(self.sampleindex_4.isslice)
        nt.ok_(self.sampleindex_5.isslice)
        nt.ok_(self.sampleindex_6.isslice)
        nt.ok_(self.sampleindex_7.isslice)
        nt.ok_(self.sampleindex_8.isslice)

    @nt.raises(exceptions.FastrValueError)
    def test_sampleindex_expand_wrong_dim(self):
        self.sampleindex_8.expand((10, 8, 9))

    def test_sampleindex_expand(self):
        # No expand used
        nt.eq_(self.sampleindex_0.expand((10,)), SampleIndex(0),)

        # Check various expands
        nt.eq_(self.sampleindex_4.expand((6, 8,)), (SampleIndex(0, 3),
                                                    SampleIndex(0, 4)))
        nt.eq_(self.sampleindex_5.expand((8, 5)), (SampleIndex(1, 3),
                                                   SampleIndex(3, 3),
                                                   SampleIndex(5, 3)))
        nt.eq_(self.sampleindex_6.expand((5,)), (SampleIndex(0),
                                                 SampleIndex(2),
                                                 SampleIndex(4)))
        nt.eq_(self.sampleindex_6.expand((6,)), (SampleIndex(0),
                                                 SampleIndex(2),
                                                 SampleIndex(4)))
        nt.eq_(self.sampleindex_6.expand((7,)), (SampleIndex(0),
                                                 SampleIndex(2),
                                                 SampleIndex(4),
                                                 SampleIndex(6)))
        nt.eq_(self.sampleindex_8.expand((7, 6)), (SampleIndex(0, 1),
                                                   SampleIndex(0, 2),
                                                   SampleIndex(0, 3),
                                                   SampleIndex(2, 1),
                                                   SampleIndex(2, 2),
                                                   SampleIndex(2, 3),
                                                   SampleIndex(4, 1),
                                                   SampleIndex(4, 2),
                                                   SampleIndex(4, 3)))

    def test_sampleindex_add(self):
        # Add sample index
        nt.eq_(self.sampleindex_0 + self.sampleindex_1, SampleIndex(0, 42, 4, 2))
        nt.eq_(self.sampleindex_2 + self.sampleindex_6, SampleIndex(5, 3, 8, slice(None, None, 2)))

        # Add element
        nt.eq_(self.sampleindex_0 + 5, SampleIndex(0, 5))
        nt.eq_(self.sampleindex_0 + slice(1, 4), SampleIndex(0, slice(1, 4)))

        # Add tuple
        nt.eq_(self.sampleindex_0 + (4, 5), SampleIndex(0, 4, 5))

    @nt.raises(TypeError)
    def test_sampleindex_add_wrong_type(self):
        self.sampleindex_0 + 1.0

    @nt.raises(exceptions.FastrTypeError)
    def test_sampleindex_add_wrong_type2(self):
        self.sampleindex_0 + (1.0, 2.0)

    def test_sampleindex_radd(self):
        # Radd element
        nt.eq_(4 + self.sampleindex_0, SampleIndex(4, 0))
        nt.eq_(slice(4, 8) + self.sampleindex_1, SampleIndex(slice(4, 8), 42, 4, 2))

        # Add tuple
        nt.eq_((1, 2) + self.sampleindex_0, SampleIndex(1, 2, 0))
        nt.eq_((slice(None, 3), 1) + self.sampleindex_2, SampleIndex(slice(None, 3), 1, 5, 3, 8))

    @nt.raises(TypeError)
    def test_sampleindex_radd_wrong_type(self):
        1.0 + self.sampleindex_0

    @nt.raises(exceptions.FastrTypeError)
    def test_sampleindex_radd_wrong_type2(self):
        (1.0, 2.0) + self.sampleindex_0

    @nt.raises(exceptions.FastrTypeError)
    def test_sampleitem_wrong_jobs_type(self):
        SampleItem((0, 1), ('a', 'b'), {0: ('val1', 'val2')}, dict())

    def test_sampleitem_repr(self):
        nt.eq_(repr(self.sample_item_0), '<SampleItem index=(0), id=single>')
        nt.eq_(repr(self.sample_item_1), '<SampleItem index=(42, 4, 2), id=test__123__test>')

    def test_sampleitem_pickle(self):
        nt.eq_(self.sample_item_0, pickle.loads(pickle.dumps(self.sample_item_0)))
        nt.eq_(self.sample_item_1, pickle.loads(pickle.dumps(self.sample_item_1)))
        nt.eq_(self.sample_item_2, pickle.loads(pickle.dumps(self.sample_item_2)))
        nt.ok_(self.sample_item_0 != pickle.loads(pickle.dumps(self.sample_item_1)))
        nt.ok_(self.sample_item_0 != pickle.loads(pickle.dumps(self.sample_item_2)))
        nt.ok_(self.sample_item_1 != pickle.loads(pickle.dumps(self.sample_item_2)))

    def test_sampleitem_newargs(self):
        nt.eq_(self.sample_item_0.__getnewargs__(), (self.sampleindex_0, self.sample_id_0, OrderedDict(), set(), set()))
        nt.eq_(self.sample_item_1.__getnewargs__(), (self.sampleindex_1, self.sample_id_1, OrderedDict({0: (String('val1'), String('val2'))}), set(), set()))
        nt.eq_(self.sample_item_2.__getnewargs__(), (SampleIndex(0, 1), SampleId('a', 'b'), OrderedDict({0: (String('val1'), String('val2'))}), set(), set()))

    def test_sampleitem_data(self):
        nt.eq_(self.sample_item_0.data, OrderedDict())
        nt.eq_(self.sample_item_1.data, OrderedDict({0: (String('val1'), String('val2'))}))
        nt.eq_(self.sample_item_2.data, OrderedDict({0: (String('val1'), String('val2'))}))
