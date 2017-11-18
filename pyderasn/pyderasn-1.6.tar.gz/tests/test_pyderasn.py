# coding: utf-8
# PyDERASN -- Python ASN.1 DER codec with abstract structures
# Copyright (C) 2017 Sergey Matveev <stargrave@stargrave.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/>.

from datetime import datetime
from string import ascii_letters
from string import printable
from string import whitespace
from unittest import TestCase

from hypothesis import assume
from hypothesis import given
from hypothesis import settings
from hypothesis.strategies import binary
from hypothesis.strategies import booleans
from hypothesis.strategies import composite
from hypothesis.strategies import data as data_strategy
from hypothesis.strategies import datetimes
from hypothesis.strategies import dictionaries
from hypothesis.strategies import integers
from hypothesis.strategies import just
from hypothesis.strategies import lists
from hypothesis.strategies import none
from hypothesis.strategies import one_of
from hypothesis.strategies import permutations
from hypothesis.strategies import sampled_from
from hypothesis.strategies import sets
from hypothesis.strategies import text
from hypothesis.strategies import tuples
from six import assertRaisesRegex
from six import byte2int
from six import indexbytes
from six import int2byte
from six import iterbytes
from six import PY2
from six import text_type

from pyderasn import _pp
from pyderasn import Any
from pyderasn import BitString
from pyderasn import BMPString
from pyderasn import Boolean
from pyderasn import BoundsError
from pyderasn import Choice
from pyderasn import decode_path_defby
from pyderasn import DecodeError
from pyderasn import Enumerated
from pyderasn import GeneralizedTime
from pyderasn import GeneralString
from pyderasn import GraphicString
from pyderasn import hexdec
from pyderasn import hexenc
from pyderasn import IA5String
from pyderasn import Integer
from pyderasn import InvalidLength
from pyderasn import InvalidOID
from pyderasn import InvalidValueType
from pyderasn import len_decode
from pyderasn import len_encode
from pyderasn import NotEnoughData
from pyderasn import Null
from pyderasn import NumericString
from pyderasn import ObjectIdentifier
from pyderasn import ObjNotReady
from pyderasn import ObjUnknown
from pyderasn import OctetString
from pyderasn import pp_console_row
from pyderasn import pprint
from pyderasn import PrintableString
from pyderasn import Sequence
from pyderasn import SequenceOf
from pyderasn import Set
from pyderasn import SetOf
from pyderasn import tag_ctxc
from pyderasn import tag_ctxp
from pyderasn import tag_decode
from pyderasn import tag_encode
from pyderasn import tag_strip
from pyderasn import TagClassApplication
from pyderasn import TagClassContext
from pyderasn import TagClassPrivate
from pyderasn import TagClassUniversal
from pyderasn import TagFormConstructed
from pyderasn import TagFormPrimitive
from pyderasn import TagMismatch
from pyderasn import TeletexString
from pyderasn import UniversalString
from pyderasn import UTCTime
from pyderasn import UTF8String
from pyderasn import VideotexString
from pyderasn import VisibleString


settings.register_profile('local', settings(
    deadline=5000,
    perform_health_check=False,
))
settings.load_profile('local')
LONG_TEST_MAX_EXAMPLES = settings().max_examples * 4

tag_classes = sampled_from((
    TagClassApplication,
    TagClassContext,
    TagClassPrivate,
    TagClassUniversal,
))
tag_forms = sampled_from((TagFormConstructed, TagFormPrimitive))


class TestHex(TestCase):
    @given(binary())
    def test_symmetric(self, data):
        self.assertEqual(hexdec(hexenc(data)), data)


class TestTagCoder(TestCase):
    @settings(max_examples=LONG_TEST_MAX_EXAMPLES)
    @given(
        tag_classes,
        tag_forms,
        integers(min_value=0, max_value=30),
        binary(max_size=5),
    )
    def test_short(self, klass, form, num, junk):
        raw = tag_encode(klass=klass, form=form, num=num)
        self.assertEqual(tag_decode(raw), (klass, form, num))
        self.assertEqual(len(raw), 1)
        self.assertEqual(
            byte2int(tag_encode(klass=klass, form=form, num=0)),
            byte2int(raw) & (1 << 7 | 1 << 6 | 1 << 5),
        )
        stripped, tlen, tail = tag_strip(memoryview(raw + junk))
        self.assertSequenceEqual(stripped.tobytes(), raw)
        self.assertEqual(tlen, len(raw))
        self.assertSequenceEqual(tail, junk)

    @settings(max_examples=LONG_TEST_MAX_EXAMPLES)
    @given(
        tag_classes,
        tag_forms,
        integers(min_value=31),
        binary(max_size=5),
    )
    def test_long(self, klass, form, num, junk):
        raw = tag_encode(klass=klass, form=form, num=num)
        self.assertEqual(tag_decode(raw), (klass, form, num))
        self.assertGreater(len(raw), 1)
        self.assertEqual(
            byte2int(tag_encode(klass=klass, form=form, num=0)) | 31,
            byte2int(raw[:1]),
        )
        self.assertEqual(byte2int(raw[-1:]) & 0x80, 0)
        self.assertTrue(all(b & 0x80 > 0 for b in iterbytes(raw[1:-1])))
        stripped, tlen, tail = tag_strip(memoryview(raw + junk))
        self.assertSequenceEqual(stripped.tobytes(), raw)
        self.assertEqual(tlen, len(raw))
        self.assertSequenceEqual(tail, junk)

    @settings(max_examples=LONG_TEST_MAX_EXAMPLES)
    @given(integers(min_value=31))
    def test_unfinished_tag(self, num):
        raw = bytearray(tag_encode(num=num))
        for i in range(1, len(raw)):
            raw[i] |= 0x80
        with assertRaisesRegex(self, DecodeError, "unfinished tag"):
            tag_strip(bytes(raw))

    def test_go_vectors_valid(self):
        for data, (eklass, etag, elen, eform) in (
                (b"\x80\x01", (TagClassContext, 0, 1, TagFormPrimitive)),
                (b"\xa0\x01", (TagClassContext, 0, 1, TagFormConstructed)),
                (b"\x02\x00", (TagClassUniversal, 2, 0, TagFormPrimitive)),
                (b"\xfe\x00", (TagClassPrivate, 30, 0, TagFormConstructed)),
                (b"\x1f\x1f\x00", (TagClassUniversal, 31, 0, TagFormPrimitive)),
                (b"\x1f\x81\x00\x00", (TagClassUniversal, 128, 0, TagFormPrimitive)),
                (b"\x1f\x81\x80\x01\x00", (TagClassUniversal, 0x4001, 0, TagFormPrimitive)),
                (b"\x00\x81\x80", (TagClassUniversal, 0, 128, TagFormPrimitive)),
                (b"\x00\x82\x01\x00", (TagClassUniversal, 0, 256, TagFormPrimitive)),
                (b"\xa0\x84\x7f\xff\xff\xff", (TagClassContext, 0, 0x7fffffff, TagFormConstructed)),
        ):
            tag, _, len_encoded = tag_strip(memoryview(data))
            klass, form, num = tag_decode(tag)
            _len, _, tail = len_decode(len_encoded)
            self.assertSequenceEqual(tail, b"")
            self.assertEqual(klass, eklass)
            self.assertEqual(num, etag)
            self.assertEqual(_len, elen)
            self.assertEqual(form, eform)

    def test_go_vectors_invalid(self):
        for data in (
                b"\x00\x83\x01\x00",
                b"\x1f\x85",
                b"\x30\x80",
                b"\xa0\x82\x00\xff",
                b"\xa0\x81\x7f",
        ):
            with self.assertRaises(DecodeError):
                _, _, len_encoded = tag_strip(memoryview(data))
                len_decode(len_encoded)

    @given(
        integers(min_value=0, max_value=127),
        integers(min_value=0, max_value=2),
    )
    def test_long_instead_of_short(self, l, dummy_num):
        octets = (b"\x00" * dummy_num) + int2byte(l)
        octets = int2byte((dummy_num + 1) | 0x80) + octets
        with self.assertRaises(DecodeError):
            len_decode(octets)


class TestLenCoder(TestCase):
    @settings(max_examples=LONG_TEST_MAX_EXAMPLES)
    @given(
        integers(min_value=0, max_value=127),
        binary(max_size=5),
    )
    def test_short(self, l, junk):
        raw = len_encode(l) + junk
        decoded, llen, tail = len_decode(memoryview(raw))
        self.assertEqual(decoded, l)
        self.assertEqual(llen, 1)
        self.assertEqual(len(raw), 1 + len(junk))
        self.assertEqual(tail.tobytes(), junk)

    @settings(max_examples=LONG_TEST_MAX_EXAMPLES)
    @given(
        integers(min_value=128),
        binary(max_size=5),
    )
    def test_long(self, l, junk):
        raw = len_encode(l) + junk
        decoded, llen, tail = len_decode(memoryview(raw))
        self.assertEqual(decoded, l)
        self.assertEqual((llen - 1) | 0x80, byte2int(raw))
        self.assertEqual(llen, len(raw) - len(junk))
        self.assertNotEqual(indexbytes(raw, 1), 0)
        self.assertSequenceEqual(tail.tobytes(), junk)

    def test_empty(self):
        with self.assertRaises(NotEnoughData):
            len_decode(b"")

    @given(integers(min_value=128))
    def test_stripped(self, _len):
        with self.assertRaises(NotEnoughData):
            len_decode(len_encode(_len)[:-1])


text_printable = text(alphabet=printable, min_size=1)


@composite
def text_letters(draw):
    result = draw(text(alphabet=ascii_letters, min_size=1))
    if PY2:
        result = result.encode("ascii")
    return result


class CommonMixin(object):
    def test_tag_default(self):
        obj = self.base_klass()
        self.assertEqual(obj.tag, obj.tag_default)

    def test_simultaneous_impl_expl(self):
        with self.assertRaises(ValueError):
            self.base_klass(impl=b"whatever", expl=b"whenever")

    @given(binary(), integers(), integers(), integers())
    def test_decoded(self, impl, offset, llen, vlen):
        obj = self.base_klass(impl=impl, _decoded=(offset, llen, vlen))
        self.assertEqual(obj.offset, offset)
        self.assertEqual(obj.llen, llen)
        self.assertEqual(obj.vlen, vlen)
        self.assertEqual(obj.tlen, len(impl))
        self.assertEqual(obj.tlvlen, obj.tlen + obj.llen + obj.vlen)

    @given(binary())
    def test_impl_inherited(self, impl_tag):
        class Inherited(self.base_klass):
            impl = impl_tag
        obj = Inherited()
        self.assertSequenceEqual(obj.impl, impl_tag)
        self.assertFalse(obj.expled)

    @given(binary())
    def test_expl_inherited(self, expl_tag):
        class Inherited(self.base_klass):
            expl = expl_tag
        obj = Inherited()
        self.assertSequenceEqual(obj.expl, expl_tag)
        self.assertTrue(obj.expled)

    def assert_copied_basic_fields(self, obj, obj_copied):
        self.assertEqual(obj, obj_copied)
        self.assertSequenceEqual(obj.tag, obj_copied.tag)
        self.assertEqual(obj.expl_tag, obj_copied.expl_tag)
        self.assertEqual(obj.default, obj_copied.default)
        self.assertEqual(obj.optional, obj_copied.optional)
        self.assertEqual(obj.offset, obj_copied.offset)
        self.assertEqual(obj.llen, obj_copied.llen)
        self.assertEqual(obj.vlen, obj_copied.vlen)


@composite
def boolean_values_strategy(draw, do_expl=False):
    value = draw(one_of(none(), booleans()))
    impl = None
    expl = None
    if do_expl:
        expl = draw(one_of(none(), integers(min_value=1).map(tag_encode)))
    else:
        impl = draw(one_of(none(), integers(min_value=1).map(tag_encode)))
    default = draw(one_of(none(), booleans()))
    optional = draw(one_of(none(), booleans()))
    _decoded = (
        draw(integers(min_value=0)),
        draw(integers(min_value=0)),
        draw(integers(min_value=0)),
    )
    return (value, impl, expl, default, optional, _decoded)


class BooleanInherited(Boolean):
    pass


class TestBoolean(CommonMixin, TestCase):
    base_klass = Boolean

    def test_invalid_value_type(self):
        with self.assertRaises(InvalidValueType) as err:
            Boolean(123)
        repr(err.exception)

    @given(booleans())
    def test_optional(self, optional):
        obj = Boolean(default=Boolean(False), optional=optional)
        self.assertTrue(obj.optional)

    @given(booleans())
    def test_ready(self, value):
        obj = Boolean()
        self.assertFalse(obj.ready)
        repr(obj)
        pprint(obj)
        with self.assertRaises(ObjNotReady) as err:
            obj.encode()
        repr(err.exception)
        obj = Boolean(value)
        self.assertTrue(obj.ready)
        repr(obj)
        pprint(obj)

    @given(booleans(), booleans(), binary(), binary())
    def test_comparison(self, value1, value2, tag1, tag2):
        for klass in (Boolean, BooleanInherited):
            obj1 = klass(value1)
            obj2 = klass(value2)
            self.assertEqual(obj1 == obj2, value1 == value2)
            self.assertEqual(obj1 != obj2, value1 != value2)
            self.assertEqual(obj1 == bool(obj2), value1 == value2)
            obj1 = klass(value1, impl=tag1)
            obj2 = klass(value1, impl=tag2)
            self.assertEqual(obj1 == obj2, tag1 == tag2)
            self.assertEqual(obj1 != obj2, tag1 != tag2)

    @given(data_strategy())
    def test_call(self, d):
        for klass in (Boolean, BooleanInherited):
            (
                value_initial,
                impl_initial,
                expl_initial,
                default_initial,
                optional_initial,
                _decoded_initial,
            ) = d.draw(boolean_values_strategy())
            obj_initial = klass(
                value_initial,
                impl_initial,
                expl_initial,
                default_initial,
                optional_initial or False,
                _decoded_initial,
            )
            (
                value,
                impl,
                expl,
                default,
                optional,
                _decoded,
            ) = d.draw(boolean_values_strategy(do_expl=impl_initial is None))
            obj = obj_initial(value, impl, expl, default, optional)
            if obj.ready:
                value_expected = default if value is None else value
                value_expected = (
                    default_initial if value_expected is None
                    else value_expected
                )
                self.assertEqual(obj, value_expected)
            self.assertEqual(obj.tag, impl or impl_initial or obj.tag_default)
            self.assertEqual(obj.expl_tag, expl or expl_initial)
            self.assertEqual(
                obj.default,
                default_initial if default is None else default,
            )
            if obj.default is None:
                optional = optional_initial if optional is None else optional
                optional = False if optional is None else optional
            else:
                optional = True
            self.assertEqual(obj.optional, optional)

    @given(boolean_values_strategy())
    def test_copy(self, values):
        for klass in (Boolean, BooleanInherited):
            obj = klass(*values)
            obj_copied = obj.copy()
            self.assert_copied_basic_fields(obj, obj_copied)

    @given(
        booleans(),
        integers(min_value=1).map(tag_encode),
    )
    def test_stripped(self, value, tag_impl):
        obj = Boolean(value, impl=tag_impl)
        with self.assertRaises(NotEnoughData):
            obj.decode(obj.encode()[:-1])

    @given(
        booleans(),
        integers(min_value=1).map(tag_ctxc),
    )
    def test_stripped_expl(self, value, tag_expl):
        obj = Boolean(value, expl=tag_expl)
        with self.assertRaises(NotEnoughData):
            obj.decode(obj.encode()[:-1])

    @given(
        integers(min_value=31),
        integers(min_value=0),
        lists(integers()),
    )
    def test_bad_tag(self, tag, offset, decode_path):
        decode_path = tuple(str(i) for i in decode_path)
        with self.assertRaises(DecodeError) as err:
            Boolean().decode(
                tag_encode(tag)[:-1],
                offset=offset,
                decode_path=decode_path,
            )
        repr(err.exception)
        self.assertEqual(err.exception.offset, offset)
        self.assertEqual(err.exception.decode_path, decode_path)

    @given(
        integers(min_value=31),
        integers(min_value=0),
        lists(integers()),
    )
    def test_bad_expl_tag(self, tag, offset, decode_path):
        decode_path = tuple(str(i) for i in decode_path)
        with self.assertRaises(DecodeError) as err:
            Boolean(expl=Boolean.tag_default).decode(
                tag_encode(tag)[:-1],
                offset=offset,
                decode_path=decode_path,
            )
        repr(err.exception)
        self.assertEqual(err.exception.offset, offset)
        self.assertEqual(err.exception.decode_path, decode_path)

    @given(
        integers(min_value=128),
        integers(min_value=0),
        lists(integers()),
    )
    def test_bad_len(self, l, offset, decode_path):
        decode_path = tuple(str(i) for i in decode_path)
        with self.assertRaises(DecodeError) as err:
            Boolean().decode(
                Boolean.tag_default + len_encode(l)[:-1],
                offset=offset,
                decode_path=decode_path,
            )
        repr(err.exception)
        self.assertEqual(err.exception.offset, offset)
        self.assertEqual(err.exception.decode_path, decode_path)

    @given(
        integers(min_value=128),
        integers(min_value=0),
        lists(integers()),
    )
    def test_bad_expl_len(self, l, offset, decode_path):
        decode_path = tuple(str(i) for i in decode_path)
        with self.assertRaises(DecodeError) as err:
            Boolean(expl=Boolean.tag_default).decode(
                Boolean.tag_default + len_encode(l)[:-1],
                offset=offset,
                decode_path=decode_path,
            )
        repr(err.exception)
        self.assertEqual(err.exception.offset, offset)
        self.assertEqual(err.exception.decode_path, decode_path)

    @settings(max_examples=LONG_TEST_MAX_EXAMPLES)
    @given(
        boolean_values_strategy(),
        booleans(),
        integers(min_value=1).map(tag_ctxc),
        integers(min_value=0),
    )
    def test_symmetric(self, values, value, tag_expl, offset):
        for klass in (Boolean, BooleanInherited):
            _, _, _, default, optional, _decoded = values
            obj = klass(
                value=value,
                default=default,
                optional=optional,
                _decoded=_decoded,
            )
            repr(obj)
            pprint(obj)
            self.assertFalse(obj.expled)
            obj_encoded = obj.encode()
            obj_expled = obj(value, expl=tag_expl)
            self.assertTrue(obj_expled.expled)
            repr(obj_expled)
            pprint(obj_expled)
            obj_expled_encoded = obj_expled.encode()
            obj_decoded, tail = obj_expled.decode(obj_expled_encoded, offset=offset)
            repr(obj_decoded)
            pprint(obj_decoded)
            self.assertEqual(tail, b"")
            self.assertEqual(obj_decoded, obj_expled)
            self.assertNotEqual(obj_decoded, obj)
            self.assertEqual(bool(obj_decoded), bool(obj_expled))
            self.assertEqual(bool(obj_decoded), bool(obj))
            self.assertSequenceEqual(obj_decoded.encode(), obj_expled_encoded)
            self.assertSequenceEqual(obj_decoded.expl_tag, tag_expl)
            self.assertEqual(obj_decoded.expl_tlen, len(tag_expl))
            self.assertEqual(
                obj_decoded.expl_llen,
                len(len_encode(len(obj_encoded))),
            )
            self.assertEqual(obj_decoded.tlvlen, len(obj_encoded))
            self.assertEqual(obj_decoded.expl_vlen, len(obj_encoded))
            self.assertEqual(
                obj_decoded.offset,
                offset + obj_decoded.expl_tlen + obj_decoded.expl_llen,
            )
            self.assertEqual(obj_decoded.expl_offset, offset)

    @given(integers(min_value=2))
    def test_invalid_len(self, l):
        with self.assertRaises(InvalidLength):
            Boolean().decode(b"".join((
                Boolean.tag_default,
                len_encode(l),
                b"\x00" * l,
            )))

    @given(integers(min_value=0 + 1, max_value=255 - 1))
    def test_invalid_value(self, value):
        with assertRaisesRegex(self, DecodeError, "unacceptable Boolean value"):
            Boolean().decode(b"".join((
                Boolean.tag_default,
                len_encode(1),
                int2byte(value),
            )))


@composite
def integer_values_strategy(draw, do_expl=False):
    bound_min, value, default, bound_max = sorted(draw(sets(
        integers(),
        min_size=4,
        max_size=4,
    )))
    if draw(booleans()):
        value = None
    _specs = None
    if draw(booleans()):
        _specs = draw(sets(text_letters()))
        values = draw(sets(
            integers(),
            min_size=len(_specs),
            max_size=len(_specs),
        ))
        _specs = list(zip(_specs, values))
    bounds = None
    if draw(booleans()):
        bounds = (bound_min, bound_max)
    impl = None
    expl = None
    if do_expl:
        expl = draw(one_of(none(), integers(min_value=1).map(tag_encode)))
    else:
        impl = draw(one_of(none(), integers(min_value=1).map(tag_encode)))
    if draw(booleans()):
        default = None
    optional = draw(one_of(none(), booleans()))
    _decoded = (
        draw(integers(min_value=0)),
        draw(integers(min_value=0)),
        draw(integers(min_value=0)),
    )
    return (value, bounds, impl, expl, default, optional, _specs, _decoded)


class IntegerInherited(Integer):
    pass


class TestInteger(CommonMixin, TestCase):
    base_klass = Integer

    def test_invalid_value_type(self):
        with self.assertRaises(InvalidValueType) as err:
            Integer(12.3)
        repr(err.exception)

    @given(sets(text_letters(), min_size=2))
    def test_unknown_name(self, names_input):
        missing = names_input.pop()

        class Int(Integer):
            schema = [(n, 123) for n in names_input]
        with self.assertRaises(ObjUnknown) as err:
            Int(missing)
        repr(err.exception)

    @given(sets(text_letters(), min_size=2))
    def test_known_name(self, names_input):
        class Int(Integer):
            schema = [(n, 123) for n in names_input]
        Int(names_input.pop())

    @given(booleans())
    def test_optional(self, optional):
        obj = Integer(default=Integer(0), optional=optional)
        self.assertTrue(obj.optional)

    @given(integers())
    def test_ready(self, value):
        obj = Integer()
        self.assertFalse(obj.ready)
        repr(obj)
        pprint(obj)
        with self.assertRaises(ObjNotReady) as err:
            obj.encode()
        repr(err.exception)
        obj = Integer(value)
        self.assertTrue(obj.ready)
        repr(obj)
        pprint(obj)
        hash(obj)

    @given(integers(), integers(), binary(), binary())
    def test_comparison(self, value1, value2, tag1, tag2):
        for klass in (Integer, IntegerInherited):
            obj1 = klass(value1)
            obj2 = klass(value2)
            self.assertEqual(obj1 == obj2, value1 == value2)
            self.assertEqual(obj1 != obj2, value1 != value2)
            self.assertEqual(obj1 == int(obj2), value1 == value2)
            obj1 = klass(value1, impl=tag1)
            obj2 = klass(value1, impl=tag2)
            self.assertEqual(obj1 == obj2, tag1 == tag2)
            self.assertEqual(obj1 != obj2, tag1 != tag2)

    @given(lists(integers()))
    def test_sorted_works(self, values):
        self.assertSequenceEqual(
            [int(v) for v in sorted(Integer(v) for v in values)],
            sorted(values),
        )

    @given(data_strategy())
    def test_named(self, d):
        names_input = list(d.draw(sets(text_letters(), min_size=1)))
        values_input = list(d.draw(sets(
            integers(),
            min_size=len(names_input),
            max_size=len(names_input),
        )))
        chosen_name = d.draw(sampled_from(names_input))
        names_input = dict(zip(names_input, values_input))

        class Int(Integer):
            schema = names_input
        _int = Int(chosen_name)
        self.assertEqual(_int.named, chosen_name)
        self.assertEqual(int(_int), names_input[chosen_name])

    @given(integers(), integers(min_value=0), integers(min_value=0))
    def test_bounds_satisfied(self, bound_min, bound_delta, value_delta):
        value = bound_min + value_delta
        bound_max = value + bound_delta
        Integer(value=value, bounds=(bound_min, bound_max))

    @given(sets(integers(), min_size=3, max_size=3))
    def test_bounds_unsatisfied(self, values):
        values = sorted(values)
        with self.assertRaises(BoundsError) as err:
            Integer(value=values[0], bounds=(values[1], values[2]))
        repr(err.exception)
        with self.assertRaises(BoundsError) as err:
            Integer(value=values[2], bounds=(values[0], values[1]))
        repr(err.exception)

    @given(data_strategy())
    def test_call(self, d):
        for klass in (Integer, IntegerInherited):
            (
                value_initial,
                bounds_initial,
                impl_initial,
                expl_initial,
                default_initial,
                optional_initial,
                _specs_initial,
                _decoded_initial,
            ) = d.draw(integer_values_strategy())
            obj_initial = klass(
                value_initial,
                bounds_initial,
                impl_initial,
                expl_initial,
                default_initial,
                optional_initial or False,
                _specs_initial,
                _decoded_initial,
            )
            (
                value,
                bounds,
                impl,
                expl,
                default,
                optional,
                _,
                _decoded,
            ) = d.draw(integer_values_strategy(do_expl=impl_initial is None))
            if (default is None) and (obj_initial.default is not None):
                bounds = None
            if (
                    (bounds is None) and
                    (value is not None) and
                    (bounds_initial is not None) and
                    not (bounds_initial[0] <= value <= bounds_initial[1])
            ):
                value = None
            if (
                    (bounds is None) and
                    (default is not None) and
                    (bounds_initial is not None) and
                    not (bounds_initial[0] <= default <= bounds_initial[1])
            ):
                default = None
            obj = obj_initial(value, bounds, impl, expl, default, optional)
            if obj.ready:
                value_expected = default if value is None else value
                value_expected = (
                    default_initial if value_expected is None
                    else value_expected
                )
                self.assertEqual(obj, value_expected)
            self.assertEqual(obj.tag, impl or impl_initial or obj.tag_default)
            self.assertEqual(obj.expl_tag, expl or expl_initial)
            self.assertEqual(
                obj.default,
                default_initial if default is None else default,
            )
            if obj.default is None:
                optional = optional_initial if optional is None else optional
                optional = False if optional is None else optional
            else:
                optional = True
            self.assertEqual(obj.optional, optional)
            self.assertEqual(
                (obj._bound_min, obj._bound_max),
                bounds or bounds_initial or (float("-inf"), float("+inf")),
            )
            self.assertEqual(
                obj.specs,
                {} if _specs_initial is None else dict(_specs_initial),
            )

    @given(integer_values_strategy())
    def test_copy(self, values):
        for klass in (Integer, IntegerInherited):
            obj = klass(*values)
            obj_copied = obj.copy()
            self.assert_copied_basic_fields(obj, obj_copied)
            self.assertEqual(obj.specs, obj_copied.specs)
            self.assertEqual(obj._bound_min, obj_copied._bound_min)
            self.assertEqual(obj._bound_max, obj_copied._bound_max)
            self.assertEqual(obj._value, obj_copied._value)

    @given(
        integers(),
        integers(min_value=1).map(tag_encode),
    )
    def test_stripped(self, value, tag_impl):
        obj = Integer(value, impl=tag_impl)
        with self.assertRaises(NotEnoughData):
            obj.decode(obj.encode()[:-1])

    @given(
        integers(),
        integers(min_value=1).map(tag_ctxc),
    )
    def test_stripped_expl(self, value, tag_expl):
        obj = Integer(value, expl=tag_expl)
        with self.assertRaises(NotEnoughData):
            obj.decode(obj.encode()[:-1])

    def test_zero_len(self):
        with self.assertRaises(NotEnoughData):
            Integer().decode(b"".join((
                Integer.tag_default,
                len_encode(0),
            )))

    @given(
        integers(min_value=31),
        integers(min_value=0),
        lists(integers()),
    )
    def test_bad_tag(self, tag, offset, decode_path):
        decode_path = tuple(str(i) for i in decode_path)
        with self.assertRaises(DecodeError) as err:
            Integer().decode(
                tag_encode(tag)[:-1],
                offset=offset,
                decode_path=decode_path,
            )
        repr(err.exception)
        self.assertEqual(err.exception.offset, offset)
        self.assertEqual(err.exception.decode_path, decode_path)

    @given(
        integers(min_value=128),
        integers(min_value=0),
        lists(integers()),
    )
    def test_bad_len(self, l, offset, decode_path):
        decode_path = tuple(str(i) for i in decode_path)
        with self.assertRaises(DecodeError) as err:
            Integer().decode(
                Integer.tag_default + len_encode(l)[:-1],
                offset=offset,
                decode_path=decode_path,
            )
        repr(err.exception)
        self.assertEqual(err.exception.offset, offset)
        self.assertEqual(err.exception.decode_path, decode_path)

    @given(
        sets(integers(), min_size=2, max_size=2),
        integers(min_value=0),
        lists(integers()),
    )
    def test_invalid_bounds_while_decoding(self, ints, offset, decode_path):
        decode_path = tuple(str(i) for i in decode_path)
        value, bound_min = list(sorted(ints))

        class Int(Integer):
            bounds = (bound_min, bound_min)
        with self.assertRaises(DecodeError) as err:
            Int().decode(
                Integer(value).encode(),
                offset=offset,
                decode_path=decode_path,
            )
        repr(err.exception)
        self.assertEqual(err.exception.offset, offset)
        self.assertEqual(err.exception.decode_path, decode_path)

    @settings(max_examples=LONG_TEST_MAX_EXAMPLES)
    @given(
        integer_values_strategy(),
        integers(),
        integers(min_value=1).map(tag_ctxc),
        integers(min_value=0),
    )
    def test_symmetric(self, values, value, tag_expl, offset):
        for klass in (Integer, IntegerInherited):
            _, _, _, _, default, optional, _, _decoded = values
            obj = klass(
                value=value,
                default=default,
                optional=optional,
                _decoded=_decoded,
            )
            repr(obj)
            pprint(obj)
            self.assertFalse(obj.expled)
            obj_encoded = obj.encode()
            obj_expled = obj(value, expl=tag_expl)
            self.assertTrue(obj_expled.expled)
            repr(obj_expled)
            pprint(obj_expled)
            obj_expled_encoded = obj_expled.encode()
            obj_decoded, tail = obj_expled.decode(obj_expled_encoded, offset=offset)
            repr(obj_decoded)
            pprint(obj_decoded)
            self.assertEqual(tail, b"")
            self.assertEqual(obj_decoded, obj_expled)
            self.assertNotEqual(obj_decoded, obj)
            self.assertEqual(int(obj_decoded), int(obj_expled))
            self.assertEqual(int(obj_decoded), int(obj))
            self.assertSequenceEqual(obj_decoded.encode(), obj_expled_encoded)
            self.assertSequenceEqual(obj_decoded.expl_tag, tag_expl)
            self.assertEqual(obj_decoded.expl_tlen, len(tag_expl))
            self.assertEqual(
                obj_decoded.expl_llen,
                len(len_encode(len(obj_encoded))),
            )
            self.assertEqual(obj_decoded.tlvlen, len(obj_encoded))
            self.assertEqual(obj_decoded.expl_vlen, len(obj_encoded))
            self.assertEqual(
                obj_decoded.offset,
                offset + obj_decoded.expl_tlen + obj_decoded.expl_llen,
            )
            self.assertEqual(obj_decoded.expl_offset, offset)

    def test_go_vectors_valid(self):
        for data, expect in ((
                (b"\x00", 0),
                (b"\x7f", 127),
                (b"\x80", -128),
                (b"\xff\x7f", -129),
                (b"\xff", -1),
                (b"\x01", 1),
                (b"\x00\xff", 255),
                (b"\xff\x00", -256),
                (b"\x01\x00", 256),
                (b"\x00\x80", 128),
                (b"\x01\x00", 256),
                (b"\x80\x00\x00\x00\x00\x00\x00\x00", -9223372036854775808),
                (b"\x80\x00\x00\x00", -2147483648),
        )):
            self.assertEqual(
                Integer().decode(b"".join((
                    Integer.tag_default,
                    len_encode(len(data)),
                    data,
                )))[0],
                expect,
            )

    def test_go_vectors_invalid(self):
        for data in ((
                b"\x00\x7f",
                b"\xff\xf0",
        )):
            with self.assertRaises(DecodeError):
                Integer().decode(b"".join((
                    Integer.tag_default,
                    len_encode(len(data)),
                    data,
                )))


@composite
def bit_string_values_strategy(draw, schema=None, value_required=False, do_expl=False):
    if schema is None:
        schema = ()
        if draw(booleans()):
            schema = draw(sets(text_letters(), min_size=1, max_size=256))
            bits = draw(sets(
                integers(min_value=0, max_value=255),
                min_size=len(schema),
                max_size=len(schema),
            ))
            schema = list(zip(schema, bits))

    def _value(value_required):
        if not value_required and draw(booleans()):
            return
        generation_choice = 0
        if value_required:
            generation_choice = draw(sampled_from((1, 2, 3)))
        if generation_choice == 1 or draw(booleans()):
            return "'%s'B" % "".join(draw(lists(
                sampled_from(("0", "1")),
                max_size=len(schema),
            )))
        elif generation_choice == 2 or draw(booleans()):
            return draw(binary(max_size=len(schema) // 8))
        elif generation_choice == 3 or draw(booleans()):
            return tuple(draw(lists(sampled_from([name for name, _ in schema]))))
        return None
    value = _value(value_required)
    default = _value(value_required=False)
    impl = None
    expl = None
    if do_expl:
        expl = draw(one_of(none(), integers(min_value=1).map(tag_encode)))
    else:
        impl = draw(one_of(none(), integers(min_value=1).map(tag_encode)))
    optional = draw(one_of(none(), booleans()))
    _decoded = (
        draw(integers(min_value=0)),
        draw(integers(min_value=0)),
        draw(integers(min_value=0)),
    )
    return (schema, value, impl, expl, default, optional, _decoded)


class BitStringInherited(BitString):
    pass


class TestBitString(CommonMixin, TestCase):
    base_klass = BitString

    @given(lists(booleans()))
    def test_b_encoding(self, bits):
        obj = BitString("'%s'B" % "".join("1" if bit else "0" for bit in bits))
        self.assertEqual(obj.bit_len, len(bits))
        self.assertSequenceEqual(list(obj), bits)
        for i, bit in enumerate(bits):
            self.assertEqual(obj[i], bit)

    @given(lists(booleans()))
    def test_out_of_bounds_bits(self, bits):
        obj = BitString("'%s'B" % "".join("1" if bit else "0" for bit in bits))
        for i in range(len(bits), len(bits) * 2):
            self.assertFalse(obj[i])

    def test_bad_b_encoding(self):
        with self.assertRaises(ValueError):
            BitString("'010120101'B")

    @given(
        integers(min_value=1, max_value=255),
        integers(min_value=1, max_value=255),
    )
    def test_named_are_stripped(self, leading_zeros, trailing_zeros):
        obj = BitString("'%s1%s'B" % (("0" * leading_zeros), ("0" * trailing_zeros)))
        self.assertEqual(obj.bit_len, leading_zeros + 1 + trailing_zeros)
        self.assertGreater(len(obj.encode()), (leading_zeros + 1 + trailing_zeros) // 8)

        class BS(BitString):
            schema = (("whatever", 0),)
        obj = BS("'%s1%s'B" % (("0" * leading_zeros), ("0" * trailing_zeros)))
        self.assertEqual(obj.bit_len, leading_zeros + 1)
        self.assertGreater(len(obj.encode()), (leading_zeros + 1) // 8)

    def test_zero_len(self):
        with self.assertRaises(NotEnoughData):
            BitString().decode(b"".join((
                BitString.tag_default,
                len_encode(0),
            )))

    def test_invalid_value_type(self):
        with self.assertRaises(InvalidValueType) as err:
            BitString(123)
        repr(err.exception)
        with self.assertRaises(InvalidValueType) as err:
            BitString(u"123")
        repr(err.exception)

    def test_obj_unknown(self):
        with self.assertRaises(ObjUnknown) as err:
            BitString(b"whatever")["whenever"]
        repr(err.exception)

    def test_get_invalid_type(self):
        with self.assertRaises(InvalidValueType) as err:
            BitString(b"whatever")[(1, 2, 3)]
        repr(err.exception)

    @given(data_strategy())
    def test_unknown_name(self, d):
        _schema = d.draw(sets(text_letters(), min_size=2, max_size=5))
        missing = _schema.pop()

        class BS(BitString):
            schema = [(n, i) for i, n in enumerate(_schema)]
        with self.assertRaises(ObjUnknown) as err:
            BS((missing,))
        repr(err.exception)

    @given(booleans())
    def test_optional(self, optional):
        obj = BitString(default=BitString(b""), optional=optional)
        self.assertTrue(obj.optional)

    @given(binary())
    def test_ready(self, value):
        obj = BitString()
        self.assertFalse(obj.ready)
        repr(obj)
        pprint(obj)
        with self.assertRaises(ObjNotReady) as err:
            obj.encode()
        repr(err.exception)
        obj = BitString(value)
        self.assertTrue(obj.ready)
        repr(obj)
        pprint(obj)

    @given(
        tuples(integers(min_value=0), binary()),
        tuples(integers(min_value=0), binary()),
        binary(),
        binary(),
    )
    def test_comparison(self, value1, value2, tag1, tag2):
        for klass in (BitString, BitStringInherited):
            obj1 = klass(value1)
            obj2 = klass(value2)
            self.assertEqual(obj1 == obj2, value1 == value2)
            self.assertEqual(obj1 != obj2, value1 != value2)
            self.assertEqual(obj1 == bytes(obj2), value1[1] == value2[1])
            obj1 = klass(value1, impl=tag1)
            obj2 = klass(value1, impl=tag2)
            self.assertEqual(obj1 == obj2, tag1 == tag2)
            self.assertEqual(obj1 != obj2, tag1 != tag2)

    @given(data_strategy())
    def test_call(self, d):
        for klass in (BitString, BitStringInherited):
            (
                schema_initial,
                value_initial,
                impl_initial,
                expl_initial,
                default_initial,
                optional_initial,
                _decoded_initial,
            ) = d.draw(bit_string_values_strategy())

            class BS(klass):
                schema = schema_initial
            obj_initial = BS(
                value=value_initial,
                impl=impl_initial,
                expl=expl_initial,
                default=default_initial,
                optional=optional_initial or False,
                _decoded=_decoded_initial,
            )
            (
                _,
                value,
                impl,
                expl,
                default,
                optional,
                _decoded,
            ) = d.draw(bit_string_values_strategy(
                schema=schema_initial,
                do_expl=impl_initial is None,
            ))
            obj = obj_initial(
                value=value,
                impl=impl,
                expl=expl,
                default=default,
                optional=optional,
            )
            self.assertEqual(obj.tag, impl or impl_initial or obj.tag_default)
            self.assertEqual(obj.expl_tag, expl or expl_initial)
            if obj.default is None:
                optional = optional_initial if optional is None else optional
                optional = False if optional is None else optional
            else:
                optional = True
            self.assertEqual(obj.optional, optional)
            self.assertEqual(obj.specs, obj_initial.specs)

    @given(bit_string_values_strategy())
    def test_copy(self, values):
        for klass in (BitString, BitStringInherited):
            _schema, value, impl, expl, default, optional, _decoded = values

            class BS(klass):
                schema = _schema
            obj = BS(
                value=value,
                impl=impl,
                expl=expl,
                default=default,
                optional=optional or False,
                _decoded=_decoded,
            )
            obj_copied = obj.copy()
            self.assert_copied_basic_fields(obj, obj_copied)
            self.assertEqual(obj.specs, obj_copied.specs)
            self.assertEqual(obj._value, obj_copied._value)

    @given(
        binary(),
        integers(min_value=1).map(tag_encode),
    )
    def test_stripped(self, value, tag_impl):
        obj = BitString(value, impl=tag_impl)
        with self.assertRaises(NotEnoughData):
            obj.decode(obj.encode()[:-1])

    @given(
        binary(),
        integers(min_value=1).map(tag_ctxc),
    )
    def test_stripped_expl(self, value, tag_expl):
        obj = BitString(value, expl=tag_expl)
        with self.assertRaises(NotEnoughData):
            obj.decode(obj.encode()[:-1])

    @given(
        integers(min_value=31),
        integers(min_value=0),
        lists(integers()),
    )
    def test_bad_tag(self, tag, offset, decode_path):
        decode_path = tuple(str(i) for i in decode_path)
        with self.assertRaises(DecodeError) as err:
            BitString().decode(
                tag_encode(tag)[:-1],
                offset=offset,
                decode_path=decode_path,
            )
        repr(err.exception)
        self.assertEqual(err.exception.offset, offset)
        self.assertEqual(err.exception.decode_path, decode_path)

    @given(
        integers(min_value=128),
        integers(min_value=0),
        lists(integers()),
    )
    def test_bad_len(self, l, offset, decode_path):
        decode_path = tuple(str(i) for i in decode_path)
        with self.assertRaises(DecodeError) as err:
            BitString().decode(
                BitString.tag_default + len_encode(l)[:-1],
                offset=offset,
                decode_path=decode_path,
            )
        repr(err.exception)
        self.assertEqual(err.exception.offset, offset)
        self.assertEqual(err.exception.decode_path, decode_path)

    @settings(max_examples=LONG_TEST_MAX_EXAMPLES)
    @given(data_strategy())
    def test_symmetric(self, d):
        (
            _schema,
            value,
            _,
            _,
            default,
            optional,
            _decoded,
        ) = d.draw(bit_string_values_strategy(value_required=True))
        tag_expl = tag_ctxc(d.draw(integers(min_value=1)))
        offset = d.draw(integers(min_value=0))
        for klass in (BitString, BitStringInherited):
            class BS(klass):
                schema = _schema
            obj = BS(
                value=value,
                default=default,
                optional=optional,
                _decoded=_decoded,
            )
            repr(obj)
            pprint(obj)
            self.assertFalse(obj.expled)
            obj_encoded = obj.encode()
            obj_expled = obj(value, expl=tag_expl)
            self.assertTrue(obj_expled.expled)
            repr(obj_expled)
            pprint(obj_expled)
            obj_expled_encoded = obj_expled.encode()
            obj_decoded, tail = obj_expled.decode(obj_expled_encoded, offset=offset)
            repr(obj_decoded)
            pprint(obj_decoded)
            self.assertEqual(tail, b"")
            self.assertEqual(obj_decoded, obj_expled)
            self.assertNotEqual(obj_decoded, obj)
            self.assertEqual(bytes(obj_decoded), bytes(obj_expled))
            self.assertEqual(bytes(obj_decoded), bytes(obj))
            self.assertSequenceEqual(obj_decoded.encode(), obj_expled_encoded)
            self.assertSequenceEqual(obj_decoded.expl_tag, tag_expl)
            self.assertEqual(obj_decoded.expl_tlen, len(tag_expl))
            self.assertEqual(
                obj_decoded.expl_llen,
                len(len_encode(len(obj_encoded))),
            )
            self.assertEqual(obj_decoded.tlvlen, len(obj_encoded))
            self.assertEqual(obj_decoded.expl_vlen, len(obj_encoded))
            self.assertEqual(
                obj_decoded.offset,
                offset + obj_decoded.expl_tlen + obj_decoded.expl_llen,
            )
            self.assertEqual(obj_decoded.expl_offset, offset)
            if isinstance(value, tuple):
                self.assertSetEqual(set(value), set(obj_decoded.named))
                for name in value:
                    obj_decoded[name]

    @given(integers(min_value=1, max_value=255))
    def test_bad_zero_value(self, pad_size):
        with self.assertRaises(DecodeError):
            BitString().decode(b"".join((
                BitString.tag_default,
                len_encode(1),
                int2byte(pad_size),
            )))

    def test_go_vectors_invalid(self):
        for data in ((
                b"\x07\x01",
                b"\x07\x40",
                b"\x08\x00",
        )):
            with self.assertRaises(DecodeError):
                BitString().decode(b"".join((
                    BitString.tag_default,
                    len_encode(2),
                    data,
                )))

    def test_go_vectors_valid(self):
        obj, _ = BitString().decode(b"".join((
            BitString.tag_default,
            len_encode(1),
            b"\x00",
        )))
        self.assertEqual(bytes(obj), b"")
        self.assertEqual(obj.bit_len, 0)

        obj, _ = BitString().decode(b"".join((
            BitString.tag_default,
            len_encode(2),
            b"\x07\x00",
        )))
        self.assertEqual(bytes(obj), b"\x00")
        self.assertEqual(obj.bit_len, 1)

        obj = BitString((16, b"\x82\x40"))
        self.assertTrue(obj[0])
        self.assertFalse(obj[1])
        self.assertTrue(obj[6])
        self.assertTrue(obj[9])
        self.assertFalse(obj[17])


@composite
def octet_string_values_strategy(draw, do_expl=False):
    bound_min, bound_max = sorted(draw(sets(
        integers(min_value=0, max_value=1 << 7),
        min_size=2,
        max_size=2,
    )))
    value = draw(one_of(
        none(),
        binary(min_size=bound_min, max_size=bound_max),
    ))
    default = draw(one_of(
        none(),
        binary(min_size=bound_min, max_size=bound_max),
    ))
    bounds = None
    if draw(booleans()):
        bounds = (bound_min, bound_max)
    impl = None
    expl = None
    if do_expl:
        expl = draw(one_of(none(), integers(min_value=1).map(tag_encode)))
    else:
        impl = draw(one_of(none(), integers(min_value=1).map(tag_encode)))
    optional = draw(one_of(none(), booleans()))
    _decoded = (
        draw(integers(min_value=0)),
        draw(integers(min_value=0)),
        draw(integers(min_value=0)),
    )
    return (value, bounds, impl, expl, default, optional, _decoded)


class OctetStringInherited(OctetString):
    pass


class TestOctetString(CommonMixin, TestCase):
    base_klass = OctetString

    def test_invalid_value_type(self):
        with self.assertRaises(InvalidValueType) as err:
            OctetString(text_type(123))
        repr(err.exception)

    @given(booleans())
    def test_optional(self, optional):
        obj = OctetString(default=OctetString(b""), optional=optional)
        self.assertTrue(obj.optional)

    @given(binary())
    def test_ready(self, value):
        obj = OctetString()
        self.assertFalse(obj.ready)
        repr(obj)
        pprint(obj)
        with self.assertRaises(ObjNotReady) as err:
            obj.encode()
        repr(err.exception)
        obj = OctetString(value)
        self.assertTrue(obj.ready)
        repr(obj)
        pprint(obj)

    @given(binary(), binary(), binary(), binary())
    def test_comparison(self, value1, value2, tag1, tag2):
        for klass in (OctetString, OctetStringInherited):
            obj1 = klass(value1)
            obj2 = klass(value2)
            self.assertEqual(obj1 == obj2, value1 == value2)
            self.assertEqual(obj1 != obj2, value1 != value2)
            self.assertEqual(obj1 == bytes(obj2), value1 == value2)
            obj1 = klass(value1, impl=tag1)
            obj2 = klass(value1, impl=tag2)
            self.assertEqual(obj1 == obj2, tag1 == tag2)
            self.assertEqual(obj1 != obj2, tag1 != tag2)

    @given(lists(binary()))
    def test_sorted_works(self, values):
        self.assertSequenceEqual(
            [bytes(v) for v in sorted(OctetString(v) for v in values)],
            sorted(values),
        )

    @given(data_strategy())
    def test_bounds_satisfied(self, d):
        bound_min = d.draw(integers(min_value=0, max_value=1 << 7))
        bound_max = d.draw(integers(min_value=bound_min, max_value=1 << 7))
        value = d.draw(binary(min_size=bound_min, max_size=bound_max))
        OctetString(value=value, bounds=(bound_min, bound_max))

    @given(data_strategy())
    def test_bounds_unsatisfied(self, d):
        bound_min = d.draw(integers(min_value=1, max_value=1 << 7))
        bound_max = d.draw(integers(min_value=bound_min, max_value=1 << 7))
        value = d.draw(binary(max_size=bound_min - 1))
        with self.assertRaises(BoundsError) as err:
            OctetString(value=value, bounds=(bound_min, bound_max))
        repr(err.exception)
        value = d.draw(binary(min_size=bound_max + 1))
        with self.assertRaises(BoundsError) as err:
            OctetString(value=value, bounds=(bound_min, bound_max))
        repr(err.exception)

    @given(data_strategy())
    def test_call(self, d):
        for klass in (OctetString, OctetStringInherited):
            (
                value_initial,
                bounds_initial,
                impl_initial,
                expl_initial,
                default_initial,
                optional_initial,
                _decoded_initial,
            ) = d.draw(octet_string_values_strategy())
            obj_initial = klass(
                value_initial,
                bounds_initial,
                impl_initial,
                expl_initial,
                default_initial,
                optional_initial or False,
                _decoded_initial,
            )
            (
                value,
                bounds,
                impl,
                expl,
                default,
                optional,
                _decoded,
            ) = d.draw(octet_string_values_strategy(do_expl=impl_initial is None))
            if (default is None) and (obj_initial.default is not None):
                bounds = None
            if (
                    (bounds is None) and
                    (value is not None) and
                    (bounds_initial is not None) and
                    not (bounds_initial[0] <= len(value) <= bounds_initial[1])
            ):
                value = None
            if (
                    (bounds is None) and
                    (default is not None) and
                    (bounds_initial is not None) and
                    not (bounds_initial[0] <= len(default) <= bounds_initial[1])
            ):
                default = None
            obj = obj_initial(value, bounds, impl, expl, default, optional)
            if obj.ready:
                value_expected = default if value is None else value
                value_expected = (
                    default_initial if value_expected is None
                    else value_expected
                )
                self.assertEqual(obj, value_expected)
            self.assertEqual(obj.tag, impl or impl_initial or obj.tag_default)
            self.assertEqual(obj.expl_tag, expl or expl_initial)
            self.assertEqual(
                obj.default,
                default_initial if default is None else default,
            )
            if obj.default is None:
                optional = optional_initial if optional is None else optional
                optional = False if optional is None else optional
            else:
                optional = True
            self.assertEqual(obj.optional, optional)
            self.assertEqual(
                (obj._bound_min, obj._bound_max),
                bounds or bounds_initial or (0, float("+inf")),
            )

    @given(octet_string_values_strategy())
    def test_copy(self, values):
        for klass in (OctetString, OctetStringInherited):
            obj = klass(*values)
            obj_copied = obj.copy()
            self.assert_copied_basic_fields(obj, obj_copied)
            self.assertEqual(obj._bound_min, obj_copied._bound_min)
            self.assertEqual(obj._bound_max, obj_copied._bound_max)
            self.assertEqual(obj._value, obj_copied._value)

    @given(
        binary(),
        integers(min_value=1).map(tag_encode),
    )
    def test_stripped(self, value, tag_impl):
        obj = OctetString(value, impl=tag_impl)
        with self.assertRaises(NotEnoughData):
            obj.decode(obj.encode()[:-1])

    @given(
        binary(),
        integers(min_value=1).map(tag_ctxc),
    )
    def test_stripped_expl(self, value, tag_expl):
        obj = OctetString(value, expl=tag_expl)
        with self.assertRaises(NotEnoughData):
            obj.decode(obj.encode()[:-1])

    @given(
        integers(min_value=31),
        integers(min_value=0),
        lists(integers()),
    )
    def test_bad_tag(self, tag, offset, decode_path):
        decode_path = tuple(str(i) for i in decode_path)
        with self.assertRaises(DecodeError) as err:
            OctetString().decode(
                tag_encode(tag)[:-1],
                offset=offset,
                decode_path=decode_path,
            )
        repr(err.exception)
        self.assertEqual(err.exception.offset, offset)
        self.assertEqual(err.exception.decode_path, decode_path)

    @given(
        integers(min_value=128),
        integers(min_value=0),
        lists(integers()),
    )
    def test_bad_len(self, l, offset, decode_path):
        decode_path = tuple(str(i) for i in decode_path)
        with self.assertRaises(DecodeError) as err:
            OctetString().decode(
                OctetString.tag_default + len_encode(l)[:-1],
                offset=offset,
                decode_path=decode_path,
            )
        repr(err.exception)
        self.assertEqual(err.exception.offset, offset)
        self.assertEqual(err.exception.decode_path, decode_path)

    @given(
        sets(integers(min_value=0, max_value=10), min_size=2, max_size=2),
        integers(min_value=0),
        lists(integers()),
    )
    def test_invalid_bounds_while_decoding(self, ints, offset, decode_path):
        decode_path = tuple(str(i) for i in decode_path)
        value, bound_min = list(sorted(ints))

        class String(OctetString):
            bounds = (bound_min, bound_min)
        with self.assertRaises(DecodeError) as err:
            String().decode(
                OctetString(b"\x00" * value).encode(),
                offset=offset,
                decode_path=decode_path,
            )
        repr(err.exception)
        self.assertEqual(err.exception.offset, offset)
        self.assertEqual(err.exception.decode_path, decode_path)

    @settings(max_examples=LONG_TEST_MAX_EXAMPLES)
    @given(
        octet_string_values_strategy(),
        binary(),
        integers(min_value=1).map(tag_ctxc),
        integers(min_value=0),
    )
    def test_symmetric(self, values, value, tag_expl, offset):
        for klass in (OctetString, OctetStringInherited):
            _, _, _, _, default, optional, _decoded = values
            obj = klass(
                value=value,
                default=default,
                optional=optional,
                _decoded=_decoded,
            )
            repr(obj)
            pprint(obj)
            self.assertFalse(obj.expled)
            obj_encoded = obj.encode()
            obj_expled = obj(value, expl=tag_expl)
            self.assertTrue(obj_expled.expled)
            repr(obj_expled)
            pprint(obj_expled)
            obj_expled_encoded = obj_expled.encode()
            obj_decoded, tail = obj_expled.decode(obj_expled_encoded, offset=offset)
            repr(obj_decoded)
            pprint(obj_decoded)
            self.assertEqual(tail, b"")
            self.assertEqual(obj_decoded, obj_expled)
            self.assertNotEqual(obj_decoded, obj)
            self.assertEqual(bytes(obj_decoded), bytes(obj_expled))
            self.assertEqual(bytes(obj_decoded), bytes(obj))
            self.assertSequenceEqual(obj_decoded.encode(), obj_expled_encoded)
            self.assertSequenceEqual(obj_decoded.expl_tag, tag_expl)
            self.assertEqual(obj_decoded.expl_tlen, len(tag_expl))
            self.assertEqual(
                obj_decoded.expl_llen,
                len(len_encode(len(obj_encoded))),
            )
            self.assertEqual(obj_decoded.tlvlen, len(obj_encoded))
            self.assertEqual(obj_decoded.expl_vlen, len(obj_encoded))
            self.assertEqual(
                obj_decoded.offset,
                offset + obj_decoded.expl_tlen + obj_decoded.expl_llen,
            )
            self.assertEqual(obj_decoded.expl_offset, offset)


@composite
def null_values_strategy(draw, do_expl=False):
    impl = None
    expl = None
    if do_expl:
        expl = draw(one_of(none(), integers(min_value=1).map(tag_encode)))
    else:
        impl = draw(one_of(none(), integers(min_value=1).map(tag_encode)))
    optional = draw(one_of(none(), booleans()))
    _decoded = (
        draw(integers(min_value=0)),
        draw(integers(min_value=0)),
        draw(integers(min_value=0)),
    )
    return (impl, expl, optional, _decoded)


class NullInherited(Null):
    pass


class TestNull(CommonMixin, TestCase):
    base_klass = Null

    def test_ready(self):
        obj = Null()
        self.assertTrue(obj.ready)
        repr(obj)
        pprint(obj)

    @given(binary(), binary())
    def test_comparison(self, tag1, tag2):
        for klass in (Null, NullInherited):
            obj1 = klass(impl=tag1)
            obj2 = klass(impl=tag2)
            self.assertEqual(obj1 == obj2, tag1 == tag2)
            self.assertEqual(obj1 != obj2, tag1 != tag2)
            self.assertNotEqual(obj1, tag2)

    @given(data_strategy())
    def test_call(self, d):
        for klass in (Null, NullInherited):
            (
                impl_initial,
                expl_initial,
                optional_initial,
                _decoded_initial,
            ) = d.draw(null_values_strategy())
            obj_initial = klass(
                impl=impl_initial,
                expl=expl_initial,
                optional=optional_initial or False,
                _decoded=_decoded_initial,
            )
            (
                impl,
                expl,
                optional,
                _decoded,
            ) = d.draw(null_values_strategy(do_expl=impl_initial is None))
            obj = obj_initial(impl=impl, expl=expl, optional=optional)
            self.assertEqual(obj.tag, impl or impl_initial or obj.tag_default)
            self.assertEqual(obj.expl_tag, expl or expl_initial)
            optional = optional_initial if optional is None else optional
            optional = False if optional is None else optional
            self.assertEqual(obj.optional, optional)

    @given(null_values_strategy())
    def test_copy(self, values):
        for klass in (Null, NullInherited):
            impl, expl, optional, _decoded = values
            obj = klass(
                impl=impl,
                expl=expl,
                optional=optional or False,
                _decoded=_decoded,
            )
            obj_copied = obj.copy()
            self.assert_copied_basic_fields(obj, obj_copied)

    @given(integers(min_value=1).map(tag_encode))
    def test_stripped(self, tag_impl):
        obj = Null(impl=tag_impl)
        with self.assertRaises(NotEnoughData):
            obj.decode(obj.encode()[:-1])

    @given(integers(min_value=1).map(tag_ctxc))
    def test_stripped_expl(self, tag_expl):
        obj = Null(expl=tag_expl)
        with self.assertRaises(NotEnoughData):
            obj.decode(obj.encode()[:-1])

    @given(
        integers(min_value=31),
        integers(min_value=0),
        lists(integers()),
    )
    def test_bad_tag(self, tag, offset, decode_path):
        decode_path = tuple(str(i) for i in decode_path)
        with self.assertRaises(DecodeError) as err:
            Null().decode(
                tag_encode(tag)[:-1],
                offset=offset,
                decode_path=decode_path,
            )
        repr(err.exception)
        self.assertEqual(err.exception.offset, offset)
        self.assertEqual(err.exception.decode_path, decode_path)

    @given(
        integers(min_value=128),
        integers(min_value=0),
        lists(integers()),
    )
    def test_bad_len(self, l, offset, decode_path):
        decode_path = tuple(str(i) for i in decode_path)
        with self.assertRaises(DecodeError) as err:
            Null().decode(
                Null.tag_default + len_encode(l)[:-1],
                offset=offset,
                decode_path=decode_path,
            )
        repr(err.exception)
        self.assertEqual(err.exception.offset, offset)
        self.assertEqual(err.exception.decode_path, decode_path)

    @given(binary(min_size=1))
    def test_tag_mismatch(self, impl):
        assume(impl != Null.tag_default)
        with self.assertRaises(TagMismatch):
            Null(impl=impl).decode(Null().encode())

    @given(
        null_values_strategy(),
        integers(min_value=1).map(tag_ctxc),
        integers(min_value=0),
    )
    def test_symmetric(self, values, tag_expl, offset):
        for klass in (Null, NullInherited):
            _, _, optional, _decoded = values
            obj = klass(optional=optional, _decoded=_decoded)
            repr(obj)
            pprint(obj)
            self.assertFalse(obj.expled)
            obj_encoded = obj.encode()
            obj_expled = obj(expl=tag_expl)
            self.assertTrue(obj_expled.expled)
            repr(obj_expled)
            pprint(obj_expled)
            obj_expled_encoded = obj_expled.encode()
            obj_decoded, tail = obj_expled.decode(obj_expled_encoded, offset=offset)
            repr(obj_decoded)
            pprint(obj_decoded)
            self.assertEqual(tail, b"")
            self.assertEqual(obj_decoded, obj_expled)
            self.assertNotEqual(obj_decoded, obj)
            self.assertSequenceEqual(obj_decoded.encode(), obj_expled_encoded)
            self.assertSequenceEqual(obj_decoded.expl_tag, tag_expl)
            self.assertEqual(obj_decoded.expl_tlen, len(tag_expl))
            self.assertEqual(
                obj_decoded.expl_llen,
                len(len_encode(len(obj_encoded))),
            )
            self.assertEqual(obj_decoded.tlvlen, len(obj_encoded))
            self.assertEqual(obj_decoded.expl_vlen, len(obj_encoded))
            self.assertEqual(
                obj_decoded.offset,
                offset + obj_decoded.expl_tlen + obj_decoded.expl_llen,
            )
            self.assertEqual(obj_decoded.expl_offset, offset)

    @given(integers(min_value=1))
    def test_invalid_len(self, l):
        with self.assertRaises(InvalidLength):
            Null().decode(b"".join((
                Null.tag_default,
                len_encode(l),
            )))


@composite
def oid_strategy(draw):
    first_arc = draw(integers(min_value=0, max_value=2))
    second_arc = 0
    if first_arc in (0, 1):
        second_arc = draw(integers(min_value=0, max_value=39))
    else:
        second_arc = draw(integers(min_value=0))
    other_arcs = draw(lists(integers(min_value=0)))
    return tuple([first_arc, second_arc] + other_arcs)


@composite
def oid_values_strategy(draw, do_expl=False):
    value = draw(one_of(none(), oid_strategy()))
    impl = None
    expl = None
    if do_expl:
        expl = draw(one_of(none(), integers(min_value=1).map(tag_encode)))
    else:
        impl = draw(one_of(none(), integers(min_value=1).map(tag_encode)))
    default = draw(one_of(none(), oid_strategy()))
    optional = draw(one_of(none(), booleans()))
    _decoded = (
        draw(integers(min_value=0)),
        draw(integers(min_value=0)),
        draw(integers(min_value=0)),
    )
    return (value, impl, expl, default, optional, _decoded)


class ObjectIdentifierInherited(ObjectIdentifier):
    pass


class TestObjectIdentifier(CommonMixin, TestCase):
    base_klass = ObjectIdentifier

    def test_invalid_value_type(self):
        with self.assertRaises(InvalidValueType) as err:
            ObjectIdentifier(123)
        repr(err.exception)

    @given(booleans())
    def test_optional(self, optional):
        obj = ObjectIdentifier(default=ObjectIdentifier("1.2.3"), optional=optional)
        self.assertTrue(obj.optional)

    @given(oid_strategy())
    def test_ready(self, value):
        obj = ObjectIdentifier()
        self.assertFalse(obj.ready)
        repr(obj)
        pprint(obj)
        with self.assertRaises(ObjNotReady) as err:
            obj.encode()
        repr(err.exception)
        obj = ObjectIdentifier(value)
        self.assertTrue(obj.ready)
        repr(obj)
        pprint(obj)
        hash(obj)

    @given(oid_strategy(), oid_strategy(), binary(), binary())
    def test_comparison(self, value1, value2, tag1, tag2):
        for klass in (ObjectIdentifier, ObjectIdentifierInherited):
            obj1 = klass(value1)
            obj2 = klass(value2)
            self.assertEqual(obj1 == obj2, value1 == value2)
            self.assertEqual(obj1 != obj2, value1 != value2)
            self.assertEqual(obj1 == tuple(obj2), value1 == value2)
            self.assertEqual(str(obj1) == str(obj2), value1 == value2)
            obj1 = klass(value1, impl=tag1)
            obj2 = klass(value1, impl=tag2)
            self.assertEqual(obj1 == obj2, tag1 == tag2)
            self.assertEqual(obj1 != obj2, tag1 != tag2)

    @given(lists(oid_strategy()))
    def test_sorted_works(self, values):
        self.assertSequenceEqual(
            [tuple(v) for v in sorted(ObjectIdentifier(v) for v in values)],
            sorted(values),
        )

    @given(data_strategy())
    def test_call(self, d):
        for klass in (ObjectIdentifier, ObjectIdentifierInherited):
            (
                value_initial,
                impl_initial,
                expl_initial,
                default_initial,
                optional_initial,
                _decoded_initial,
            ) = d.draw(oid_values_strategy())
            obj_initial = klass(
                value=value_initial,
                impl=impl_initial,
                expl=expl_initial,
                default=default_initial,
                optional=optional_initial or False,
                _decoded=_decoded_initial,
            )
            (
                value,
                impl,
                expl,
                default,
                optional,
                _decoded,
            ) = d.draw(oid_values_strategy(do_expl=impl_initial is None))
            obj = obj_initial(
                value=value,
                impl=impl,
                expl=expl,
                default=default,
                optional=optional,
            )
            if obj.ready:
                value_expected = default if value is None else value
                value_expected = (
                    default_initial if value_expected is None
                    else value_expected
                )
                self.assertEqual(obj, value_expected)
            self.assertEqual(obj.tag, impl or impl_initial or obj.tag_default)
            self.assertEqual(obj.expl_tag, expl or expl_initial)
            self.assertEqual(
                obj.default,
                default_initial if default is None else default,
            )
            if obj.default is None:
                optional = optional_initial if optional is None else optional
                optional = False if optional is None else optional
            else:
                optional = True
            self.assertEqual(obj.optional, optional)

    @given(oid_values_strategy())
    def test_copy(self, values):
        for klass in (ObjectIdentifier, ObjectIdentifierInherited):
            (
                value,
                impl,
                expl,
                default,
                optional,
                _decoded,
            ) = values
            obj = klass(
                value=value,
                impl=impl,
                expl=expl,
                default=default,
                optional=optional,
                _decoded=_decoded,
            )
            obj_copied = obj.copy()
            self.assert_copied_basic_fields(obj, obj_copied)
            self.assertEqual(obj._value, obj_copied._value)

    @settings(max_examples=LONG_TEST_MAX_EXAMPLES)
    @given(
        oid_strategy(),
        integers(min_value=1).map(tag_encode),
    )
    def test_stripped(self, value, tag_impl):
        obj = ObjectIdentifier(value, impl=tag_impl)
        with self.assertRaises(NotEnoughData):
            obj.decode(obj.encode()[:-1])

    @given(
        oid_strategy(),
        integers(min_value=1).map(tag_ctxc),
    )
    def test_stripped_expl(self, value, tag_expl):
        obj = ObjectIdentifier(value, expl=tag_expl)
        with self.assertRaises(NotEnoughData):
            obj.decode(obj.encode()[:-1])

    @given(
        integers(min_value=31),
        integers(min_value=0),
        lists(integers()),
    )
    def test_bad_tag(self, tag, offset, decode_path):
        decode_path = tuple(str(i) for i in decode_path)
        with self.assertRaises(DecodeError) as err:
            ObjectIdentifier().decode(
                tag_encode(tag)[:-1],
                offset=offset,
                decode_path=decode_path,
            )
        repr(err.exception)
        self.assertEqual(err.exception.offset, offset)
        self.assertEqual(err.exception.decode_path, decode_path)

    @given(
        integers(min_value=128),
        integers(min_value=0),
        lists(integers()),
    )
    def test_bad_len(self, l, offset, decode_path):
        decode_path = tuple(str(i) for i in decode_path)
        with self.assertRaises(DecodeError) as err:
            ObjectIdentifier().decode(
                ObjectIdentifier.tag_default + len_encode(l)[:-1],
                offset=offset,
                decode_path=decode_path,
            )
        repr(err.exception)
        self.assertEqual(err.exception.offset, offset)
        self.assertEqual(err.exception.decode_path, decode_path)

    def test_zero_oid(self):
        with self.assertRaises(NotEnoughData):
            ObjectIdentifier().decode(
                b"".join((ObjectIdentifier.tag_default, len_encode(0)))
            )

    @settings(max_examples=LONG_TEST_MAX_EXAMPLES)
    @given(oid_strategy())
    def test_unfinished_oid(self, value):
        assume(list(value)[-1] > 255)
        obj_encoded = ObjectIdentifier(value).encode()
        obj, _ = ObjectIdentifier().decode(obj_encoded)
        data = obj_encoded[obj.tlen + obj.llen:-1]
        data = b"".join((
            ObjectIdentifier.tag_default,
            len_encode(len(data)),
            data,
        ))
        with assertRaisesRegex(self, DecodeError, "unfinished OID"):
            obj.decode(data)

    @given(integers(min_value=0))
    def test_invalid_short(self, value):
        with self.assertRaises(InvalidOID):
            ObjectIdentifier((value,))
        with self.assertRaises(InvalidOID):
            ObjectIdentifier("%d" % value)

    @given(integers(min_value=3), integers(min_value=0))
    def test_invalid_first_arc(self, first_arc, second_arc):
        with self.assertRaises(InvalidOID):
            ObjectIdentifier((first_arc, second_arc))
        with self.assertRaises(InvalidOID):
            ObjectIdentifier("%d.%d" % (first_arc, second_arc))

    @given(integers(min_value=0, max_value=1), integers(min_value=40))
    def test_invalid_second_arc(self, first_arc, second_arc):
        with self.assertRaises(InvalidOID):
            ObjectIdentifier((first_arc, second_arc))
        with self.assertRaises(InvalidOID):
            ObjectIdentifier("%d.%d" % (first_arc, second_arc))

    @given(text(alphabet=ascii_letters + ".", min_size=1))
    def test_junk(self, oid):
        with self.assertRaises(InvalidOID):
            ObjectIdentifier(oid)

    @settings(max_examples=LONG_TEST_MAX_EXAMPLES)
    @given(oid_strategy())
    def test_validness(self, oid):
        obj = ObjectIdentifier(oid)
        self.assertEqual(obj, ObjectIdentifier(".".join(str(arc) for arc in oid)))
        str(obj)
        repr(obj)
        pprint(obj)

    @settings(max_examples=LONG_TEST_MAX_EXAMPLES)
    @given(
        oid_values_strategy(),
        oid_strategy(),
        integers(min_value=1).map(tag_ctxc),
        integers(min_value=0),
    )
    def test_symmetric(self, values, value, tag_expl, offset):
        for klass in (ObjectIdentifier, ObjectIdentifierInherited):
            _, _, _, default, optional, _decoded = values
            obj = klass(
                value=value,
                default=default,
                optional=optional,
                _decoded=_decoded,
            )
            repr(obj)
            pprint(obj)
            self.assertFalse(obj.expled)
            obj_encoded = obj.encode()
            obj_expled = obj(value, expl=tag_expl)
            self.assertTrue(obj_expled.expled)
            repr(obj_expled)
            pprint(obj_expled)
            obj_expled_encoded = obj_expled.encode()
            obj_decoded, tail = obj_expled.decode(obj_expled_encoded, offset=offset)
            repr(obj_decoded)
            pprint(obj_decoded)
            self.assertEqual(tail, b"")
            self.assertEqual(obj_decoded, obj_expled)
            self.assertNotEqual(obj_decoded, obj)
            self.assertEqual(tuple(obj_decoded), tuple(obj_expled))
            self.assertEqual(tuple(obj_decoded), tuple(obj))
            self.assertSequenceEqual(obj_decoded.encode(), obj_expled_encoded)
            self.assertSequenceEqual(obj_decoded.expl_tag, tag_expl)
            self.assertEqual(obj_decoded.expl_tlen, len(tag_expl))
            self.assertEqual(
                obj_decoded.expl_llen,
                len(len_encode(len(obj_encoded))),
            )
            self.assertEqual(obj_decoded.tlvlen, len(obj_encoded))
            self.assertEqual(obj_decoded.expl_vlen, len(obj_encoded))
            self.assertEqual(
                obj_decoded.offset,
                offset + obj_decoded.expl_tlen + obj_decoded.expl_llen,
            )
            self.assertEqual(obj_decoded.expl_offset, offset)

    @given(
        oid_strategy().map(ObjectIdentifier),
        oid_strategy().map(ObjectIdentifier),
    )
    def test_add(self, oid1, oid2):
        oid_expect = ObjectIdentifier(str(oid1) + "." + str(oid2))
        for oid_to_add in (oid2, tuple(oid2)):
            self.assertEqual(oid1 + oid_to_add, oid_expect)
        with self.assertRaises(InvalidValueType):
            oid1 + str(oid2)

    def test_go_vectors_valid(self):
        for data, expect in (
                (b"\x55", (2, 5)),
                (b"\x55\x02", (2, 5, 2)),
                (b"\x55\x02\xc0\x00", (2, 5, 2, 8192)),
                (b"\x81\x34\x03", (2, 100, 3)),
        ):
            self.assertEqual(
                ObjectIdentifier().decode(b"".join((
                    ObjectIdentifier.tag_default,
                    len_encode(len(data)),
                    data,
                )))[0],
                expect,
            )

    def test_go_vectors_invalid(self):
        data = b"\x55\x02\xc0\x80\x80\x80\x80"
        with self.assertRaises(DecodeError):
            ObjectIdentifier().decode(b"".join((
                Integer.tag_default,
                len_encode(len(data)),
                data,
            )))


@composite
def enumerated_values_strategy(draw, schema=None, do_expl=False):
    if schema is None:
        schema = list(draw(sets(text_printable, min_size=1, max_size=3)))
        values = list(draw(sets(
            integers(),
            min_size=len(schema),
            max_size=len(schema),
        )))
        schema = list(zip(schema, values))
    value = draw(one_of(none(), sampled_from([k for k, v in schema])))
    impl = None
    expl = None
    if do_expl:
        expl = draw(one_of(none(), integers(min_value=1).map(tag_encode)))
    else:
        impl = draw(one_of(none(), integers(min_value=1).map(tag_encode)))
    default = draw(one_of(none(), sampled_from([v for k, v in schema])))
    optional = draw(one_of(none(), booleans()))
    _decoded = (
        draw(integers(min_value=0)),
        draw(integers(min_value=0)),
        draw(integers(min_value=0)),
    )
    return (schema, value, impl, expl, default, optional, _decoded)


class TestEnumerated(CommonMixin, TestCase):
    class EWhatever(Enumerated):
        schema = (("whatever", 0),)

    base_klass = EWhatever

    def test_schema_required(self):
        with assertRaisesRegex(self, ValueError, "schema must be specified"):
            Enumerated()

    def test_invalid_value_type(self):
        with self.assertRaises(InvalidValueType) as err:
            self.base_klass((1, 2))
        repr(err.exception)

    @given(sets(text_letters(), min_size=2))
    def test_unknown_name(self, schema_input):
        missing = schema_input.pop()

        class E(Enumerated):
            schema = [(n, 123) for n in schema_input]
        with self.assertRaises(ObjUnknown) as err:
            E(missing)
        repr(err.exception)

    @given(
        sets(text_letters(), min_size=2),
        sets(integers(), min_size=2),
    )
    def test_unknown_value(self, schema_input, values_input):
        schema_input.pop()
        missing_value = values_input.pop()
        _input = list(zip(schema_input, values_input))

        class E(Enumerated):
            schema = _input
        with self.assertRaises(DecodeError) as err:
            E(missing_value)
        repr(err.exception)

    @given(booleans())
    def test_optional(self, optional):
        obj = self.base_klass(default="whatever", optional=optional)
        self.assertTrue(obj.optional)

    def test_ready(self):
        obj = self.base_klass()
        self.assertFalse(obj.ready)
        repr(obj)
        pprint(obj)
        with self.assertRaises(ObjNotReady) as err:
            obj.encode()
        repr(err.exception)
        obj = self.base_klass("whatever")
        self.assertTrue(obj.ready)
        repr(obj)
        pprint(obj)

    @given(integers(), integers(), binary(), binary())
    def test_comparison(self, value1, value2, tag1, tag2):
        class E(Enumerated):
            schema = (
                ("whatever0", value1),
                ("whatever1", value2),
            )

        class EInherited(E):
            pass
        for klass in (E, EInherited):
            obj1 = klass(value1)
            obj2 = klass(value2)
            self.assertEqual(obj1 == obj2, value1 == value2)
            self.assertEqual(obj1 != obj2, value1 != value2)
            self.assertEqual(obj1 == int(obj2), value1 == value2)
            obj1 = klass(value1, impl=tag1)
            obj2 = klass(value1, impl=tag2)
            self.assertEqual(obj1 == obj2, tag1 == tag2)
            self.assertEqual(obj1 != obj2, tag1 != tag2)

    @given(data_strategy())
    def test_call(self, d):
        (
            schema_initial,
            value_initial,
            impl_initial,
            expl_initial,
            default_initial,
            optional_initial,
            _decoded_initial,
        ) = d.draw(enumerated_values_strategy())

        class E(Enumerated):
            schema = schema_initial
        obj_initial = E(
            value=value_initial,
            impl=impl_initial,
            expl=expl_initial,
            default=default_initial,
            optional=optional_initial or False,
            _decoded=_decoded_initial,
        )
        (
            _,
            value,
            impl,
            expl,
            default,
            optional,
            _decoded,
        ) = d.draw(enumerated_values_strategy(
            schema=schema_initial,
            do_expl=impl_initial is None,
        ))
        obj = obj_initial(
            value=value,
            impl=impl,
            expl=expl,
            default=default,
            optional=optional,
        )
        if obj.ready:
            value_expected = default if value is None else value
            value_expected = (
                default_initial if value_expected is None
                else value_expected
            )
            self.assertEqual(
                int(obj),
                dict(schema_initial).get(value_expected, value_expected),
            )
        self.assertEqual(obj.tag, impl or impl_initial or obj.tag_default)
        self.assertEqual(obj.expl_tag, expl or expl_initial)
        self.assertEqual(
            obj.default,
            default_initial if default is None else default,
        )
        if obj.default is None:
            optional = optional_initial if optional is None else optional
            optional = False if optional is None else optional
        else:
            optional = True
        self.assertEqual(obj.optional, optional)
        self.assertEqual(obj.specs, dict(schema_initial))

    @given(enumerated_values_strategy())
    def test_copy(self, values):
        schema_input, value, impl, expl, default, optional, _decoded = values

        class E(Enumerated):
            schema = schema_input
        obj = E(
            value=value,
            impl=impl,
            expl=expl,
            default=default,
            optional=optional,
            _decoded=_decoded,
        )
        obj_copied = obj.copy()
        self.assert_copied_basic_fields(obj, obj_copied)
        self.assertEqual(obj.specs, obj_copied.specs)

    @settings(max_examples=LONG_TEST_MAX_EXAMPLES)
    @given(data_strategy())
    def test_symmetric(self, d):
        schema_input, _, _, _, default, optional, _decoded = d.draw(
            enumerated_values_strategy(),
        )
        tag_expl = d.draw(integers(min_value=1).map(tag_ctxc))
        offset = d.draw(integers(min_value=0))
        value = d.draw(sampled_from(sorted([v for _, v in schema_input])))

        class E(Enumerated):
            schema = schema_input
        obj = E(
            value=value,
            default=default,
            optional=optional,
            _decoded=_decoded,
        )
        repr(obj)
        pprint(obj)
        self.assertFalse(obj.expled)
        obj_encoded = obj.encode()
        obj_expled = obj(value, expl=tag_expl)
        self.assertTrue(obj_expled.expled)
        repr(obj_expled)
        pprint(obj_expled)
        obj_expled_encoded = obj_expled.encode()
        obj_decoded, tail = obj_expled.decode(obj_expled_encoded, offset=offset)
        repr(obj_decoded)
        pprint(obj_decoded)
        self.assertEqual(tail, b"")
        self.assertEqual(obj_decoded, obj_expled)
        self.assertNotEqual(obj_decoded, obj)
        self.assertEqual(int(obj_decoded), int(obj_expled))
        self.assertEqual(int(obj_decoded), int(obj))
        self.assertSequenceEqual(obj_decoded.encode(), obj_expled_encoded)
        self.assertEqual(obj_decoded.expl_tag, tag_expl)
        self.assertEqual(obj_decoded.expl_tlen, len(tag_expl))
        self.assertEqual(
            obj_decoded.expl_llen,
            len(len_encode(len(obj_encoded))),
        )
        self.assertEqual(obj_decoded.tlvlen, len(obj_encoded))
        self.assertEqual(obj_decoded.expl_vlen, len(obj_encoded))
        self.assertEqual(
            obj_decoded.offset,
            offset + obj_decoded.expl_tlen + obj_decoded.expl_llen,
        )
        self.assertEqual(obj_decoded.expl_offset, offset)


@composite
def string_values_strategy(draw, alphabet, do_expl=False):
    bound_min, bound_max = sorted(draw(sets(
        integers(min_value=0, max_value=1 << 7),
        min_size=2,
        max_size=2,
    )))
    value = draw(one_of(
        none(),
        text(alphabet=alphabet, min_size=bound_min, max_size=bound_max),
    ))
    default = draw(one_of(
        none(),
        text(alphabet=alphabet, min_size=bound_min, max_size=bound_max),
    ))
    bounds = None
    if draw(booleans()):
        bounds = (bound_min, bound_max)
    impl = None
    expl = None
    if do_expl:
        expl = draw(one_of(none(), integers(min_value=1).map(tag_encode)))
    else:
        impl = draw(one_of(none(), integers(min_value=1).map(tag_encode)))
    optional = draw(one_of(none(), booleans()))
    _decoded = (
        draw(integers(min_value=0)),
        draw(integers(min_value=0)),
        draw(integers(min_value=0)),
    )
    return (value, bounds, impl, expl, default, optional, _decoded)


class StringMixin(object):
    def test_invalid_value_type(self):
        with self.assertRaises(InvalidValueType) as err:
            self.base_klass((1, 2))
        repr(err.exception)

    def text_alphabet(self):
        if self.base_klass.encoding in ("ascii", "iso-8859-1"):
            return printable + whitespace
        return None

    @given(booleans())
    def test_optional(self, optional):
        obj = self.base_klass(default=self.base_klass(""), optional=optional)
        self.assertTrue(obj.optional)

    @given(data_strategy())
    def test_ready(self, d):
        obj = self.base_klass()
        self.assertFalse(obj.ready)
        repr(obj)
        pprint(obj)
        text_type(obj)
        with self.assertRaises(ObjNotReady) as err:
            obj.encode()
        repr(err.exception)
        value = d.draw(text(alphabet=self.text_alphabet()))
        obj = self.base_klass(value)
        self.assertTrue(obj.ready)
        repr(obj)
        pprint(obj)
        text_type(obj)

    @given(data_strategy())
    def test_comparison(self, d):
        value1 = d.draw(text(alphabet=self.text_alphabet()))
        value2 = d.draw(text(alphabet=self.text_alphabet()))
        tag1 = d.draw(binary())
        tag2 = d.draw(binary())
        obj1 = self.base_klass(value1)
        obj2 = self.base_klass(value2)
        self.assertEqual(obj1 == obj2, value1 == value2)
        self.assertEqual(obj1 != obj2, value1 != value2)
        self.assertEqual(obj1 == bytes(obj2), value1 == value2)
        self.assertEqual(obj1 == text_type(obj2), value1 == value2)
        obj1 = self.base_klass(value1, impl=tag1)
        obj2 = self.base_klass(value1, impl=tag2)
        self.assertEqual(obj1 == obj2, tag1 == tag2)
        self.assertEqual(obj1 != obj2, tag1 != tag2)

    @given(data_strategy())
    def test_bounds_satisfied(self, d):
        bound_min = d.draw(integers(min_value=0, max_value=1 << 7))
        bound_max = d.draw(integers(min_value=bound_min, max_value=1 << 7))
        value = d.draw(text(
            alphabet=self.text_alphabet(),
            min_size=bound_min,
            max_size=bound_max,
        ))
        self.base_klass(value=value, bounds=(bound_min, bound_max))

    @given(data_strategy())
    def test_bounds_unsatisfied(self, d):
        bound_min = d.draw(integers(min_value=1, max_value=1 << 7))
        bound_max = d.draw(integers(min_value=bound_min, max_value=1 << 7))
        value = d.draw(text(alphabet=self.text_alphabet(), max_size=bound_min - 1))
        with self.assertRaises(BoundsError) as err:
            self.base_klass(value=value, bounds=(bound_min, bound_max))
        repr(err.exception)
        value = d.draw(text(alphabet=self.text_alphabet(), min_size=bound_max + 1))
        with self.assertRaises(BoundsError) as err:
            self.base_klass(value=value, bounds=(bound_min, bound_max))
        repr(err.exception)

    @given(data_strategy())
    def test_call(self, d):
        (
            value_initial,
            bounds_initial,
            impl_initial,
            expl_initial,
            default_initial,
            optional_initial,
            _decoded_initial,
        ) = d.draw(string_values_strategy(self.text_alphabet()))
        obj_initial = self.base_klass(
            value_initial,
            bounds_initial,
            impl_initial,
            expl_initial,
            default_initial,
            optional_initial or False,
            _decoded_initial,
        )
        (
            value,
            bounds,
            impl,
            expl,
            default,
            optional,
            _decoded,
        ) = d.draw(string_values_strategy(
            self.text_alphabet(),
            do_expl=impl_initial is None,
        ))
        if (default is None) and (obj_initial.default is not None):
            bounds = None
        if (
                (bounds is None) and
                (value is not None) and
                (bounds_initial is not None) and
                not (bounds_initial[0] <= len(value) <= bounds_initial[1])
        ):
            value = None
        if (
                (bounds is None) and
                (default is not None) and
                (bounds_initial is not None) and
                not (bounds_initial[0] <= len(default) <= bounds_initial[1])
        ):
            default = None
        obj = obj_initial(value, bounds, impl, expl, default, optional)
        if obj.ready:
            value_expected = default if value is None else value
            value_expected = (
                default_initial if value_expected is None
                else value_expected
            )
            self.assertEqual(obj, value_expected)
        self.assertEqual(obj.tag, impl or impl_initial or obj.tag_default)
        self.assertEqual(obj.expl_tag, expl or expl_initial)
        self.assertEqual(
            obj.default,
            default_initial if default is None else default,
        )
        if obj.default is None:
            optional = optional_initial if optional is None else optional
            optional = False if optional is None else optional
        else:
            optional = True
        self.assertEqual(obj.optional, optional)
        self.assertEqual(
            (obj._bound_min, obj._bound_max),
            bounds or bounds_initial or (0, float("+inf")),
        )

    @given(data_strategy())
    def test_copy(self, d):
        values = d.draw(string_values_strategy(self.text_alphabet()))
        obj = self.base_klass(*values)
        obj_copied = obj.copy()
        self.assert_copied_basic_fields(obj, obj_copied)
        self.assertEqual(obj._bound_min, obj_copied._bound_min)
        self.assertEqual(obj._bound_max, obj_copied._bound_max)
        self.assertEqual(obj._value, obj_copied._value)

    @given(data_strategy())
    def test_stripped(self, d):
        value = d.draw(text(alphabet=self.text_alphabet()))
        tag_impl = tag_encode(d.draw(integers(min_value=1)))
        obj = self.base_klass(value, impl=tag_impl)
        with self.assertRaises(NotEnoughData):
            obj.decode(obj.encode()[:-1])

    @given(data_strategy())
    def test_stripped_expl(self, d):
        value = d.draw(text(alphabet=self.text_alphabet()))
        tag_expl = tag_ctxc(d.draw(integers(min_value=1)))
        obj = self.base_klass(value, expl=tag_expl)
        with self.assertRaises(NotEnoughData):
            obj.decode(obj.encode()[:-1])

    @given(
        integers(min_value=31),
        integers(min_value=0),
        lists(integers()),
    )
    def test_bad_tag(self, tag, offset, decode_path):
        decode_path = tuple(str(i) for i in decode_path)
        with self.assertRaises(DecodeError) as err:
            self.base_klass().decode(
                tag_encode(tag)[:-1],
                offset=offset,
                decode_path=decode_path,
            )
        repr(err.exception)
        self.assertEqual(err.exception.offset, offset)
        self.assertEqual(err.exception.decode_path, decode_path)

    @given(
        integers(min_value=128),
        integers(min_value=0),
        lists(integers()),
    )
    def test_bad_len(self, l, offset, decode_path):
        decode_path = tuple(str(i) for i in decode_path)
        with self.assertRaises(DecodeError) as err:
            self.base_klass().decode(
                self.base_klass.tag_default + len_encode(l)[:-1],
                offset=offset,
                decode_path=decode_path,
            )
        repr(err.exception)
        self.assertEqual(err.exception.offset, offset)
        self.assertEqual(err.exception.decode_path, decode_path)

    @given(
        sets(integers(min_value=0, max_value=10), min_size=2, max_size=2),
        integers(min_value=0),
        lists(integers()),
    )
    def test_invalid_bounds_while_decoding(self, ints, offset, decode_path):
        decode_path = tuple(str(i) for i in decode_path)
        value, bound_min = list(sorted(ints))

        class String(self.base_klass):
            # Multiply this value by four, to satisfy UTF-32 bounds
            # (4 bytes per character) validation
            bounds = (bound_min * 4, bound_min * 4)
        with self.assertRaises(DecodeError) as err:
            String().decode(
                self.base_klass(b"\x00\x00\x00\x00" * value).encode(),
                offset=offset,
                decode_path=decode_path,
            )
        repr(err.exception)
        self.assertEqual(err.exception.offset, offset)
        self.assertEqual(err.exception.decode_path, decode_path)

    @given(data_strategy())
    def test_symmetric(self, d):
        values = d.draw(string_values_strategy(self.text_alphabet()))
        value = d.draw(text(alphabet=self.text_alphabet()))
        tag_expl = tag_ctxc(d.draw(integers(min_value=1)))
        offset = d.draw(integers(min_value=0))
        _, _, _, _, default, optional, _decoded = values
        obj = self.base_klass(
            value=value,
            default=default,
            optional=optional,
            _decoded=_decoded,
        )
        repr(obj)
        pprint(obj)
        self.assertFalse(obj.expled)
        obj_encoded = obj.encode()
        obj_expled = obj(value, expl=tag_expl)
        self.assertTrue(obj_expled.expled)
        repr(obj_expled)
        pprint(obj_expled)
        obj_expled_encoded = obj_expled.encode()
        obj_decoded, tail = obj_expled.decode(obj_expled_encoded, offset=offset)
        repr(obj_decoded)
        pprint(obj_decoded)
        self.assertEqual(tail, b"")
        self.assertEqual(obj_decoded, obj_expled)
        self.assertNotEqual(obj_decoded, obj)
        self.assertEqual(bytes(obj_decoded), bytes(obj_expled))
        self.assertEqual(bytes(obj_decoded), bytes(obj))
        self.assertEqual(text_type(obj_decoded), text_type(obj_expled))
        self.assertEqual(text_type(obj_decoded), text_type(obj))
        self.assertSequenceEqual(obj_decoded.encode(), obj_expled_encoded)
        self.assertSequenceEqual(obj_decoded.expl_tag, tag_expl)
        self.assertEqual(obj_decoded.expl_tlen, len(tag_expl))
        self.assertEqual(
            obj_decoded.expl_llen,
            len(len_encode(len(obj_encoded))),
        )
        self.assertEqual(obj_decoded.tlvlen, len(obj_encoded))
        self.assertEqual(obj_decoded.expl_vlen, len(obj_encoded))
        self.assertEqual(
            obj_decoded.offset,
            offset + obj_decoded.expl_tlen + obj_decoded.expl_llen,
        )
        self.assertEqual(obj_decoded.expl_offset, offset)


class TestUTF8String(StringMixin, CommonMixin, TestCase):
    base_klass = UTF8String


class TestNumericString(StringMixin, CommonMixin, TestCase):
    base_klass = NumericString


class TestPrintableString(StringMixin, CommonMixin, TestCase):
    base_klass = PrintableString


class TestTeletexString(StringMixin, CommonMixin, TestCase):
    base_klass = TeletexString


class TestVideotexString(StringMixin, CommonMixin, TestCase):
    base_klass = VideotexString


class TestIA5String(StringMixin, CommonMixin, TestCase):
    base_klass = IA5String


class TestGraphicString(StringMixin, CommonMixin, TestCase):
    base_klass = GraphicString


class TestVisibleString(StringMixin, CommonMixin, TestCase):
    base_klass = VisibleString


class TestGeneralString(StringMixin, CommonMixin, TestCase):
    base_klass = GeneralString


class TestUniversalString(StringMixin, CommonMixin, TestCase):
    base_klass = UniversalString


class TestBMPString(StringMixin, CommonMixin, TestCase):
    base_klass = BMPString


@composite
def generalized_time_values_strategy(
        draw,
        min_datetime,
        max_datetime,
        omit_ms=False,
        do_expl=False,
):
    value = None
    if draw(booleans()):
        value = draw(datetimes(min_value=min_datetime, max_value=max_datetime))
        if omit_ms:
            value = value.replace(microsecond=0)
    default = None
    if draw(booleans()):
        default = draw(datetimes(min_value=min_datetime, max_value=max_datetime))
        if omit_ms:
            default = default.replace(microsecond=0)
    impl = None
    expl = None
    if do_expl:
        expl = draw(one_of(none(), integers(min_value=1).map(tag_encode)))
    else:
        impl = draw(one_of(none(), integers(min_value=1).map(tag_encode)))
    optional = draw(one_of(none(), booleans()))
    _decoded = (
        draw(integers(min_value=0)),
        draw(integers(min_value=0)),
        draw(integers(min_value=0)),
    )
    return (value, impl, expl, default, optional, _decoded)


class TimeMixin(object):
    def test_invalid_value_type(self):
        with self.assertRaises(InvalidValueType) as err:
            self.base_klass(datetime.now().timetuple())
        repr(err.exception)

    @given(data_strategy())
    def test_optional(self, d):
        default = d.draw(datetimes(
            min_value=self.min_datetime,
            max_value=self.max_datetime,
        ))
        optional = d.draw(booleans())
        obj = self.base_klass(default=default, optional=optional)
        self.assertTrue(obj.optional)

    @given(data_strategy())
    def test_ready(self, d):
        obj = self.base_klass()
        self.assertFalse(obj.ready)
        repr(obj)
        pprint(obj)
        with self.assertRaises(ObjNotReady) as err:
            obj.encode()
        repr(err.exception)
        value = d.draw(datetimes(min_value=self.min_datetime))
        obj = self.base_klass(value)
        self.assertTrue(obj.ready)
        repr(obj)
        pprint(obj)

    @given(data_strategy())
    def test_comparison(self, d):
        value1 = d.draw(datetimes(
            min_value=self.min_datetime,
            max_value=self.max_datetime,
        ))
        value2 = d.draw(datetimes(
            min_value=self.min_datetime,
            max_value=self.max_datetime,
        ))
        tag1 = d.draw(binary())
        tag2 = d.draw(binary())
        if self.omit_ms:
            value1 = value1.replace(microsecond=0)
            value2 = value2.replace(microsecond=0)
        obj1 = self.base_klass(value1)
        obj2 = self.base_klass(value2)
        self.assertEqual(obj1 == obj2, value1 == value2)
        self.assertEqual(obj1 != obj2, value1 != value2)
        self.assertEqual(obj1 == obj2.todatetime(), value1 == value2)
        self.assertEqual(obj1 == bytes(obj2), value1 == value2)
        obj1 = self.base_klass(value1, impl=tag1)
        obj2 = self.base_klass(value1, impl=tag2)
        self.assertEqual(obj1 == obj2, tag1 == tag2)
        self.assertEqual(obj1 != obj2, tag1 != tag2)

    @given(data_strategy())
    def test_call(self, d):
        (
            value_initial,
            impl_initial,
            expl_initial,
            default_initial,
            optional_initial,
            _decoded_initial,
        ) = d.draw(generalized_time_values_strategy(
            min_datetime=self.min_datetime,
            max_datetime=self.max_datetime,
            omit_ms=self.omit_ms,
        ))
        obj_initial = self.base_klass(
            value=value_initial,
            impl=impl_initial,
            expl=expl_initial,
            default=default_initial,
            optional=optional_initial or False,
            _decoded=_decoded_initial,
        )
        (
            value,
            impl,
            expl,
            default,
            optional,
            _decoded,
        ) = d.draw(generalized_time_values_strategy(
            min_datetime=self.min_datetime,
            max_datetime=self.max_datetime,
            omit_ms=self.omit_ms,
            do_expl=impl_initial is None,
        ))
        obj = obj_initial(
            value=value,
            impl=impl,
            expl=expl,
            default=default,
            optional=optional,
        )
        if obj.ready:
            value_expected = default if value is None else value
            value_expected = (
                default_initial if value_expected is None
                else value_expected
            )
            self.assertEqual(obj, value_expected)
        self.assertEqual(obj.tag, impl or impl_initial or obj.tag_default)
        self.assertEqual(obj.expl_tag, expl or expl_initial)
        self.assertEqual(
            obj.default,
            default_initial if default is None else default,
        )
        if obj.default is None:
            optional = optional_initial if optional is None else optional
            optional = False if optional is None else optional
        else:
            optional = True
        self.assertEqual(obj.optional, optional)

    @given(data_strategy())
    def test_copy(self, d):
        values = d.draw(generalized_time_values_strategy(
            min_datetime=self.min_datetime,
            max_datetime=self.max_datetime,
        ))
        obj = self.base_klass(*values)
        obj_copied = obj.copy()
        self.assert_copied_basic_fields(obj, obj_copied)
        self.assertEqual(obj._value, obj_copied._value)

    @given(data_strategy())
    def test_stripped(self, d):
        value = d.draw(datetimes(
            min_value=self.min_datetime,
            max_value=self.max_datetime,
        ))
        tag_impl = tag_encode(d.draw(integers(min_value=1)))
        obj = self.base_klass(value, impl=tag_impl)
        with self.assertRaises(NotEnoughData):
            obj.decode(obj.encode()[:-1])

    @given(data_strategy())
    def test_stripped_expl(self, d):
        value = d.draw(datetimes(
            min_value=self.min_datetime,
            max_value=self.max_datetime,
        ))
        tag_expl = tag_ctxc(d.draw(integers(min_value=1)))
        obj = self.base_klass(value, expl=tag_expl)
        with self.assertRaises(NotEnoughData):
            obj.decode(obj.encode()[:-1])

    @settings(max_examples=LONG_TEST_MAX_EXAMPLES)
    @given(data_strategy())
    def test_symmetric(self, d):
        values = d.draw(generalized_time_values_strategy(
            min_datetime=self.min_datetime,
            max_datetime=self.max_datetime,
        ))
        value = d.draw(datetimes(
            min_value=self.min_datetime,
            max_value=self.max_datetime,
        ))
        tag_expl = tag_ctxc(d.draw(integers(min_value=1)))
        offset = d.draw(integers(min_value=0))
        _, _, _, default, optional, _decoded = values
        obj = self.base_klass(
            value=value,
            default=default,
            optional=optional,
            _decoded=_decoded,
        )
        repr(obj)
        pprint(obj)
        self.assertFalse(obj.expled)
        obj_encoded = obj.encode()
        obj_expled = obj(value, expl=tag_expl)
        self.assertTrue(obj_expled.expled)
        repr(obj_expled)
        pprint(obj_expled)
        obj_expled_encoded = obj_expled.encode()
        obj_decoded, tail = obj_expled.decode(obj_expled_encoded, offset=offset)
        repr(obj_decoded)
        pprint(obj_decoded)
        self.assertEqual(tail, b"")
        self.assertEqual(obj_decoded, obj_expled)
        self.assertEqual(obj_decoded.todatetime(), obj_expled.todatetime())
        self.assertEqual(obj_decoded.todatetime(), obj.todatetime())
        self.assertSequenceEqual(obj_decoded.encode(), obj_expled_encoded)
        self.assertSequenceEqual(obj_decoded.expl_tag, tag_expl)
        self.assertEqual(obj_decoded.expl_tlen, len(tag_expl))
        self.assertEqual(
            obj_decoded.expl_llen,
            len(len_encode(len(obj_encoded))),
        )
        self.assertEqual(obj_decoded.tlvlen, len(obj_encoded))
        self.assertEqual(obj_decoded.expl_vlen, len(obj_encoded))
        self.assertEqual(
            obj_decoded.offset,
            offset + obj_decoded.expl_tlen + obj_decoded.expl_llen,
        )
        self.assertEqual(obj_decoded.expl_offset, offset)


class TestGeneralizedTime(TimeMixin, CommonMixin, TestCase):
    base_klass = GeneralizedTime
    omit_ms = False
    min_datetime = datetime(1900, 1, 1)
    max_datetime = datetime(9999, 12, 31)

    def test_go_vectors_invalid(self):
        for data in ((
                b"20100102030405",
                b"00000100000000Z",
                b"20101302030405Z",
                b"20100002030405Z",
                b"20100100030405Z",
                b"20100132030405Z",
                b"20100231030405Z",
                b"20100102240405Z",
                b"20100102036005Z",
                b"20100102030460Z",
                b"-20100102030410Z",
                b"2010-0102030410Z",
                b"2010-0002030410Z",
                b"201001-02030410Z",
                b"20100102-030410Z",
                b"2010010203-0410Z",
                b"201001020304-10Z",
                # These ones are INVALID in *DER*, but accepted
                # by Go's encoding/asn1
                b"20100102030405+0607",
                b"20100102030405-0607",
        )):
            with self.assertRaises(DecodeError) as err:
                GeneralizedTime(data)
            repr(err.exception)

    def test_go_vectors_valid(self):
        self.assertEqual(
            GeneralizedTime(b"20100102030405Z").todatetime(),
            datetime(2010, 1, 2, 3, 4, 5, 0),
        )


class TestUTCTime(TimeMixin, CommonMixin, TestCase):
    base_klass = UTCTime
    omit_ms = True
    min_datetime = datetime(2000, 1, 1)
    max_datetime = datetime(2049, 12, 31)

    def test_go_vectors_invalid(self):
        for data in ((
                b"a10506234540Z",
                b"91a506234540Z",
                b"9105a6234540Z",
                b"910506a34540Z",
                b"910506334a40Z",
                b"91050633444aZ",
                b"910506334461Z",
                b"910506334400Za",
                b"000100000000Z",
                b"101302030405Z",
                b"100002030405Z",
                b"100100030405Z",
                b"100132030405Z",
                b"100231030405Z",
                b"100102240405Z",
                b"100102036005Z",
                b"100102030460Z",
                b"-100102030410Z",
                b"10-0102030410Z",
                b"10-0002030410Z",
                b"1001-02030410Z",
                b"100102-030410Z",
                b"10010203-0410Z",
                b"1001020304-10Z",
                # These ones are INVALID in *DER*, but accepted
                # by Go's encoding/asn1
                b"910506164540-0700",
                b"910506164540+0730",
                b"9105062345Z",
                b"5105062345Z",
        )):
            with self.assertRaises(DecodeError) as err:
                UTCTime(data)
            repr(err.exception)

    def test_go_vectors_valid(self):
        self.assertEqual(
            UTCTime(b"910506234540Z").todatetime(),
            datetime(1991, 5, 6, 23, 45, 40, 0),
        )

    @given(integers(min_value=0, max_value=49))
    def test_pre50(self, year):
        self.assertEqual(
            UTCTime(("%02d1231235959Z" % year).encode("ascii")).todatetime().year,
            2000 + year,
        )

    @given(integers(min_value=50, max_value=99))
    def test_post50(self, year):
        self.assertEqual(
            UTCTime(("%02d1231235959Z" % year).encode("ascii")).todatetime().year,
            1900 + year,
        )


@composite
def any_values_strategy(draw, do_expl=False):
    value = draw(one_of(none(), binary()))
    expl = None
    if do_expl:
        expl = draw(one_of(none(), integers(min_value=1).map(tag_encode)))
    optional = draw(one_of(none(), booleans()))
    _decoded = (
        draw(integers(min_value=0)),
        draw(integers(min_value=0)),
        draw(integers(min_value=0)),
    )
    return (value, expl, optional, _decoded)


class AnyInherited(Any):
    pass


class TestAny(CommonMixin, TestCase):
    base_klass = Any

    def test_invalid_value_type(self):
        with self.assertRaises(InvalidValueType) as err:
            Any(123)
        repr(err.exception)

    @given(booleans())
    def test_optional(self, optional):
        obj = Any(optional=optional)
        self.assertEqual(obj.optional, optional)

    @given(binary())
    def test_ready(self, value):
        obj = Any()
        self.assertFalse(obj.ready)
        repr(obj)
        pprint(obj)
        with self.assertRaises(ObjNotReady) as err:
            obj.encode()
        repr(err.exception)
        obj = Any(value)
        self.assertTrue(obj.ready)
        repr(obj)
        pprint(obj)

    @given(integers())
    def test_basic(self, value):
        integer_encoded = Integer(value).encode()
        for obj in (
                Any(integer_encoded),
                Any(Integer(value)),
                Any(Any(Integer(value))),
        ):
            self.assertSequenceEqual(bytes(obj), integer_encoded)
            self.assertEqual(
                obj.decode(obj.encode())[0].vlen,
                len(integer_encoded),
            )
            repr(obj)
            pprint(obj)
            self.assertSequenceEqual(obj.encode(), integer_encoded)

    @given(binary(), binary())
    def test_comparison(self, value1, value2):
        for klass in (Any, AnyInherited):
            obj1 = klass(value1)
            obj2 = klass(value2)
            self.assertEqual(obj1 == obj2, value1 == value2)
            self.assertEqual(obj1 != obj2, value1 != value2)
            self.assertEqual(obj1 == bytes(obj2), value1 == value2)

    @given(data_strategy())
    def test_call(self, d):
        for klass in (Any, AnyInherited):
            (
                value_initial,
                expl_initial,
                optional_initial,
                _decoded_initial,
            ) = d.draw(any_values_strategy())
            obj_initial = klass(
                value_initial,
                expl_initial,
                optional_initial or False,
                _decoded_initial,
            )
            (
                value,
                expl,
                optional,
                _decoded,
            ) = d.draw(any_values_strategy(do_expl=True))
            obj = obj_initial(value, expl, optional)
            if obj.ready:
                value_expected = None if value is None else value
                self.assertEqual(obj, value_expected)
            self.assertEqual(obj.expl_tag, expl or expl_initial)
            if obj.default is None:
                optional = optional_initial if optional is None else optional
                optional = False if optional is None else optional
            self.assertEqual(obj.optional, optional)

    def test_simultaneous_impl_expl(self):
        # override it, as Any does not have implicit tag
        pass

    def test_decoded(self):
        # override it, as Any does not have implicit tag
        pass

    @given(any_values_strategy())
    def test_copy(self, values):
        for klass in (Any, AnyInherited):
            obj = klass(*values)
            obj_copied = obj.copy()
            self.assert_copied_basic_fields(obj, obj_copied)
            self.assertEqual(obj._value, obj_copied._value)

    @given(binary().map(OctetString))
    def test_stripped(self, value):
        obj = Any(value)
        with self.assertRaises(NotEnoughData):
            obj.decode(obj.encode()[:-1])

    @given(
        binary(),
        integers(min_value=1).map(tag_ctxc),
    )
    def test_stripped_expl(self, value, tag_expl):
        obj = Any(value, expl=tag_expl)
        with self.assertRaises(NotEnoughData):
            obj.decode(obj.encode()[:-1])

    @given(
        integers(min_value=31),
        integers(min_value=0),
        lists(integers()),
    )
    def test_bad_tag(self, tag, offset, decode_path):
        decode_path = tuple(str(i) for i in decode_path)
        with self.assertRaises(DecodeError) as err:
            Any().decode(
                tag_encode(tag)[:-1],
                offset=offset,
                decode_path=decode_path,
            )
        repr(err.exception)
        self.assertEqual(err.exception.offset, offset)
        self.assertEqual(err.exception.decode_path, decode_path)

    @given(
        integers(min_value=128),
        integers(min_value=0),
        lists(integers()),
    )
    def test_bad_len(self, l, offset, decode_path):
        decode_path = tuple(str(i) for i in decode_path)
        with self.assertRaises(DecodeError) as err:
            Any().decode(
                Any.tag_default + len_encode(l)[:-1],
                offset=offset,
                decode_path=decode_path,
            )
        repr(err.exception)
        self.assertEqual(err.exception.offset, offset)
        self.assertEqual(err.exception.decode_path, decode_path)

    @settings(max_examples=LONG_TEST_MAX_EXAMPLES)
    @given(
        any_values_strategy(),
        integers().map(lambda x: Integer(x).encode()),
        integers(min_value=1).map(tag_ctxc),
        integers(min_value=0),
    )
    def test_symmetric(self, values, value, tag_expl, offset):
        for klass in (Any, AnyInherited):
            _, _, optional, _decoded = values
            obj = klass(value=value, optional=optional, _decoded=_decoded)
            repr(obj)
            pprint(obj)
            self.assertFalse(obj.expled)
            obj_encoded = obj.encode()
            obj_expled = obj(value, expl=tag_expl)
            self.assertTrue(obj_expled.expled)
            repr(obj_expled)
            pprint(obj_expled)
            obj_expled_encoded = obj_expled.encode()
            obj_decoded, tail = obj_expled.decode(obj_expled_encoded, offset=offset)
            repr(obj_decoded)
            pprint(obj_decoded)
            self.assertEqual(tail, b"")
            self.assertEqual(obj_decoded, obj_expled)
            self.assertEqual(bytes(obj_decoded), bytes(obj_expled))
            self.assertEqual(bytes(obj_decoded), bytes(obj))
            self.assertSequenceEqual(obj_decoded.encode(), obj_expled_encoded)
            self.assertSequenceEqual(obj_decoded.expl_tag, tag_expl)
            self.assertEqual(obj_decoded.expl_tlen, len(tag_expl))
            self.assertEqual(
                obj_decoded.expl_llen,
                len(len_encode(len(obj_encoded))),
            )
            self.assertEqual(obj_decoded.tlvlen, len(obj_encoded))
            self.assertEqual(obj_decoded.expl_vlen, len(obj_encoded))
            self.assertEqual(
                obj_decoded.offset,
                offset + obj_decoded.expl_tlen + obj_decoded.expl_llen,
            )
            self.assertEqual(obj_decoded.expl_offset, offset)
            self.assertEqual(obj_decoded.tlen, 0)
            self.assertEqual(obj_decoded.llen, 0)
            self.assertEqual(obj_decoded.vlen, len(value))


@composite
def choice_values_strategy(draw, value_required=False, schema=None, do_expl=False):
    if schema is None:
        names = list(draw(sets(text_letters(), min_size=1, max_size=5)))
        tags = [tag_encode(tag) for tag in draw(sets(
            integers(min_value=0),
            min_size=len(names),
            max_size=len(names),
        ))]
        schema = [(name, Integer(impl=tag)) for name, tag in zip(names, tags)]
    value = None
    if value_required or draw(booleans()):
        value = draw(tuples(
            sampled_from([name for name, _ in schema]),
            integers().map(Integer),
        ))
    expl = None
    if do_expl:
        expl = draw(one_of(none(), integers(min_value=1).map(tag_encode)))
    default = draw(one_of(
        none(),
        tuples(sampled_from([name for name, _ in schema]), integers().map(Integer)),
    ))
    optional = draw(one_of(none(), booleans()))
    _decoded = (
        draw(integers(min_value=0)),
        draw(integers(min_value=0)),
        draw(integers(min_value=0)),
    )
    return (schema, value, expl, default, optional, _decoded)


class ChoiceInherited(Choice):
    pass


class TestChoice(CommonMixin, TestCase):
    class Wahl(Choice):
        schema = (("whatever", Boolean()),)
    base_klass = Wahl

    def test_schema_required(self):
        with assertRaisesRegex(self, ValueError, "schema must be specified"):
            Choice()

    def test_impl_forbidden(self):
        with assertRaisesRegex(self, ValueError, "no implicit tag allowed"):
            Choice(impl=b"whatever")

    def test_invalid_value_type(self):
        with self.assertRaises(InvalidValueType) as err:
            self.base_klass(123)
        repr(err.exception)
        with self.assertRaises(ObjUnknown) as err:
            self.base_klass(("whenever", Boolean(False)))
        repr(err.exception)
        with self.assertRaises(InvalidValueType) as err:
            self.base_klass(("whatever", Integer(123)))
        repr(err.exception)

    @given(booleans())
    def test_optional(self, optional):
        obj = self.base_klass(
            default=self.base_klass(("whatever", Boolean(False))),
            optional=optional,
        )
        self.assertTrue(obj.optional)

    @given(booleans())
    def test_ready(self, value):
        obj = self.base_klass()
        self.assertFalse(obj.ready)
        repr(obj)
        pprint(obj)
        self.assertIsNone(obj["whatever"])
        with self.assertRaises(ObjNotReady) as err:
            obj.encode()
        repr(err.exception)
        obj["whatever"] = Boolean()
        self.assertFalse(obj.ready)
        repr(obj)
        pprint(obj)
        obj["whatever"] = Boolean(value)
        self.assertTrue(obj.ready)
        repr(obj)
        pprint(obj)

    @given(booleans(), booleans())
    def test_comparison(self, value1, value2):
        class WahlInherited(self.base_klass):
            pass
        for klass in (self.base_klass, WahlInherited):
            obj1 = klass(("whatever", Boolean(value1)))
            obj2 = klass(("whatever", Boolean(value2)))
            self.assertEqual(obj1 == obj2, value1 == value2)
            self.assertEqual(obj1 != obj2, value1 != value2)
            self.assertEqual(obj1 == obj2._value, value1 == value2)
            self.assertFalse(obj1 == obj2._value[1])

    @given(data_strategy())
    def test_call(self, d):
        for klass in (Choice, ChoiceInherited):
            (
                schema_initial,
                value_initial,
                expl_initial,
                default_initial,
                optional_initial,
                _decoded_initial,
            ) = d.draw(choice_values_strategy())

            class Wahl(klass):
                schema = schema_initial
            obj_initial = Wahl(
                value=value_initial,
                expl=expl_initial,
                default=default_initial,
                optional=optional_initial or False,
                _decoded=_decoded_initial,
            )
            (
                _,
                value,
                expl,
                default,
                optional,
                _decoded,
            ) = d.draw(choice_values_strategy(schema=schema_initial, do_expl=True))
            obj = obj_initial(value, expl, default, optional)
            if obj.ready:
                value_expected = default if value is None else value
                value_expected = (
                    default_initial if value_expected is None
                    else value_expected
                )
                self.assertEqual(obj.choice, value_expected[0])
                self.assertEqual(obj.value, int(value_expected[1]))
            self.assertEqual(obj.expl_tag, expl or expl_initial)
            default_expect = default_initial if default is None else default
            if default_expect is not None:
                self.assertEqual(obj.default.choice, default_expect[0])
                self.assertEqual(obj.default.value, int(default_expect[1]))
            if obj.default is None:
                optional = optional_initial if optional is None else optional
                optional = False if optional is None else optional
            else:
                optional = True
            self.assertEqual(obj.optional, optional)
            self.assertEqual(obj.specs, obj_initial.specs)

    def test_simultaneous_impl_expl(self):
        # override it, as Any does not have implicit tag
        pass

    def test_decoded(self):
        # override it, as Any does not have implicit tag
        pass

    @given(choice_values_strategy())
    def test_copy(self, values):
        _schema, value, expl, default, optional, _decoded = values

        class Wahl(self.base_klass):
            schema = _schema
        obj = Wahl(
            value=value,
            expl=expl,
            default=default,
            optional=optional or False,
            _decoded=_decoded,
        )
        obj_copied = obj.copy()
        self.assertIsNone(obj.tag)
        self.assertIsNone(obj_copied.tag)
        # hack for assert_copied_basic_fields
        obj.tag = "whatever"
        obj_copied.tag = "whatever"
        self.assert_copied_basic_fields(obj, obj_copied)
        self.assertEqual(obj._value, obj_copied._value)
        self.assertEqual(obj.specs, obj_copied.specs)

    @given(booleans())
    def test_stripped(self, value):
        obj = self.base_klass(("whatever", Boolean(value)))
        with self.assertRaises(NotEnoughData):
            obj.decode(obj.encode()[:-1])

    @given(
        booleans(),
        integers(min_value=1).map(tag_ctxc),
    )
    def test_stripped_expl(self, value, tag_expl):
        obj = self.base_klass(("whatever", Boolean(value)), expl=tag_expl)
        with self.assertRaises(NotEnoughData):
            obj.decode(obj.encode()[:-1])

    @settings(max_examples=LONG_TEST_MAX_EXAMPLES)
    @given(data_strategy())
    def test_symmetric(self, d):
        _schema, value, _, default, optional, _decoded = d.draw(
            choice_values_strategy(value_required=True)
        )
        tag_expl = tag_ctxc(d.draw(integers(min_value=1)))
        offset = d.draw(integers(min_value=0))

        class Wahl(self.base_klass):
            schema = _schema
        obj = Wahl(
            value=value,
            default=default,
            optional=optional,
            _decoded=_decoded,
        )
        repr(obj)
        pprint(obj)
        self.assertFalse(obj.expled)
        obj_encoded = obj.encode()
        obj_expled = obj(value, expl=tag_expl)
        self.assertTrue(obj_expled.expled)
        repr(obj_expled)
        pprint(obj_expled)
        obj_expled_encoded = obj_expled.encode()
        obj_decoded, tail = obj_expled.decode(obj_expled_encoded, offset=offset)
        repr(obj_decoded)
        pprint(obj_decoded)
        self.assertEqual(tail, b"")
        self.assertEqual(obj_decoded, obj_expled)
        self.assertEqual(obj_decoded.choice, obj_expled.choice)
        self.assertEqual(obj_decoded.value, obj_expled.value)
        self.assertEqual(obj_decoded.choice, obj.choice)
        self.assertEqual(obj_decoded.value, obj.value)
        self.assertSequenceEqual(obj_decoded.encode(), obj_expled_encoded)
        self.assertSequenceEqual(obj_decoded.expl_tag, tag_expl)
        self.assertEqual(obj_decoded.expl_tlen, len(tag_expl))
        self.assertEqual(
            obj_decoded.expl_llen,
            len(len_encode(len(obj_encoded))),
        )
        self.assertEqual(obj_decoded.tlvlen, len(obj_encoded))
        self.assertEqual(obj_decoded.expl_vlen, len(obj_encoded))
        self.assertEqual(
            obj_decoded.offset,
            offset + obj_decoded.expl_tlen + obj_decoded.expl_llen,
        )
        self.assertEqual(obj_decoded.expl_offset, offset)
        self.assertSequenceEqual(
            obj_expled_encoded[
                obj_decoded.value.offset - offset:
                obj_decoded.value.offset + obj_decoded.value.tlvlen - offset
            ],
            obj_encoded,
        )

    @given(integers())
    def test_set_get(self, value):
        class Wahl(Choice):
            schema = (
                ("erste", Boolean()),
                ("zweite", Integer()),
            )
        obj = Wahl()
        with self.assertRaises(ObjUnknown) as err:
            obj["whatever"] = "whenever"
        with self.assertRaises(InvalidValueType) as err:
            obj["zweite"] = Boolean(False)
        obj["zweite"] = Integer(value)
        repr(err.exception)
        with self.assertRaises(ObjUnknown) as err:
            obj["whatever"]
        repr(err.exception)
        self.assertIsNone(obj["erste"])
        self.assertEqual(obj["zweite"], Integer(value))

    def test_tag_mismatch(self):
        class Wahl(Choice):
            schema = (
                ("erste", Boolean()),
            )
        int_encoded = Integer(123).encode()
        bool_encoded = Boolean(False).encode()
        obj = Wahl()
        obj.decode(bool_encoded)
        with self.assertRaises(TagMismatch):
            obj.decode(int_encoded)


@composite
def seq_values_strategy(draw, seq_klass, do_expl=False):
    value = None
    if draw(booleans()):
        value = seq_klass()
        value._value = {
            k: v for k, v in draw(dictionaries(
                integers(),
                one_of(
                    booleans().map(Boolean),
                    integers().map(Integer),
                ),
            )).items()
        }
    schema = None
    if draw(booleans()):
        schema = list(draw(dictionaries(
            integers(),
            one_of(
                booleans().map(Boolean),
                integers().map(Integer),
            ),
        )).items())
    impl = None
    expl = None
    if do_expl:
        expl = draw(one_of(none(), integers(min_value=1).map(tag_encode)))
    else:
        impl = draw(one_of(none(), integers(min_value=1).map(tag_encode)))
    default = None
    if draw(booleans()):
        default = seq_klass()
        default._value = {
            k: v for k, v in draw(dictionaries(
                integers(),
                one_of(
                    booleans().map(Boolean),
                    integers().map(Integer),
                ),
            )).items()
        }
    optional = draw(one_of(none(), booleans()))
    _decoded = (
        draw(integers(min_value=0)),
        draw(integers(min_value=0)),
        draw(integers(min_value=0)),
    )
    return (value, schema, impl, expl, default, optional, _decoded)


@composite
def sequence_strategy(draw, seq_klass):
    inputs = draw(lists(
        one_of(
            tuples(just(Boolean), booleans(), one_of(none(), booleans())),
            tuples(just(Integer), integers(), one_of(none(), integers())),
        ),
        max_size=6,
    ))
    tags = draw(sets(
        integers(min_value=1),
        min_size=len(inputs),
        max_size=len(inputs),
    ))
    inits = [
        ({"expl": tag_ctxc(tag)} if expled else {"impl": tag_encode(tag)})
        for tag, expled in zip(tags, draw(lists(
            booleans(),
            min_size=len(inputs),
            max_size=len(inputs),
        )))
    ]
    empties = []
    for i, optional in enumerate(draw(lists(
            sampled_from(("required", "optional", "empty")),
            min_size=len(inputs),
            max_size=len(inputs),
    ))):
        if optional in ("optional", "empty"):
            inits[i]["optional"] = True
        if optional == "empty":
            empties.append(i)
    empties = set(empties)
    names = list(draw(sets(
        text_printable,
        min_size=len(inputs),
        max_size=len(inputs),
    )))
    schema = []
    for i, (klass, value, default) in enumerate(inputs):
        schema.append((names[i], klass(default=default, **inits[i])))
    seq_name = draw(text_letters())
    Seq = type(seq_name, (seq_klass,), {"schema": tuple(schema)})
    seq = Seq()
    expects = []
    for i, (klass, value, default) in enumerate(inputs):
        name = names[i]
        _, spec = schema[i]
        expect = {
            "name": name,
            "optional": False,
            "presented": False,
            "default_value": None if spec.default is None else default,
            "value": None,
        }
        if i in empties:
            expect["optional"] = True
        else:
            expect["presented"] = True
            expect["value"] = value
            if spec.optional:
                expect["optional"] = True
            if default is not None and default == value:
                expect["presented"] = False
            seq[name] = klass(value)
        expects.append(expect)
    return seq, expects


@composite
def sequences_strategy(draw, seq_klass):
    tags = draw(sets(integers(min_value=1), min_size=0, max_size=5))
    inits = [
        ({"expl": tag_ctxc(tag)} if expled else {"impl": tag_encode(tag)})
        for tag, expled in zip(tags, draw(lists(
            booleans(),
            min_size=len(tags),
            max_size=len(tags),
        )))
    ]
    defaulted = set(
        i for i, is_default in enumerate(draw(lists(
            booleans(),
            min_size=len(tags),
            max_size=len(tags),
        ))) if is_default
    )
    names = list(draw(sets(
        text_printable,
        min_size=len(tags),
        max_size=len(tags),
    )))
    seq_expectses = draw(lists(
        sequence_strategy(seq_klass=seq_klass),
        min_size=len(tags),
        max_size=len(tags),
    ))
    seqs = [seq for seq, _ in seq_expectses]
    schema = []
    for i, (name, seq) in enumerate(zip(names, seqs)):
        schema.append((
            name,
            seq(default=(seq if i in defaulted else None), **inits[i]),
        ))
    seq_name = draw(text_letters())
    Seq = type(seq_name, (seq_klass,), {"schema": tuple(schema)})
    seq_outer = Seq()
    expect_outers = []
    for name, (seq_inner, expects_inner) in zip(names, seq_expectses):
        expect = {
            "name": name,
            "expects": expects_inner,
            "presented": False,
        }
        seq_outer[name] = seq_inner
        if seq_outer.specs[name].default is None:
            expect["presented"] = True
        expect_outers.append(expect)
    return seq_outer, expect_outers


class SeqMixing(object):
    def test_invalid_value_type(self):
        with self.assertRaises(InvalidValueType) as err:
            self.base_klass((1, 2, 3))
        repr(err.exception)

    def test_invalid_value_type_set(self):
        class Seq(self.base_klass):
            schema = (("whatever", Boolean()),)
        seq = Seq()
        with self.assertRaises(InvalidValueType) as err:
            seq["whatever"] = Integer(123)
        repr(err.exception)

    @given(booleans())
    def test_optional(self, optional):
        obj = self.base_klass(default=self.base_klass(), optional=optional)
        self.assertTrue(obj.optional)

    @given(data_strategy())
    def test_ready(self, d):
        ready = {
            str(i): v for i, v in enumerate(d.draw(lists(
                booleans(),
                min_size=1,
                max_size=3,
            )))
        }
        non_ready = {
            str(i + len(ready)): v for i, v in enumerate(d.draw(lists(
                booleans(),
                min_size=1,
                max_size=3,
            )))
        }
        schema_input = []
        for name in d.draw(permutations(
                list(ready.keys()) + list(non_ready.keys()),
        )):
            schema_input.append((name, Boolean()))

        class Seq(self.base_klass):
            schema = tuple(schema_input)
        seq = Seq()
        for name in ready.keys():
            seq[name]
            seq[name] = Boolean()
        self.assertFalse(seq.ready)
        repr(seq)
        pprint(seq)
        for name, value in ready.items():
            seq[name] = Boolean(value)
        self.assertFalse(seq.ready)
        repr(seq)
        pprint(seq)
        with self.assertRaises(ObjNotReady) as err:
            seq.encode()
        repr(err.exception)
        for name, value in non_ready.items():
            seq[name] = Boolean(value)
        self.assertTrue(seq.ready)
        repr(seq)
        pprint(seq)

    @given(data_strategy())
    def test_call(self, d):
        class SeqInherited(self.base_klass):
            pass
        for klass in (self.base_klass, SeqInherited):
            (
                value_initial,
                schema_initial,
                impl_initial,
                expl_initial,
                default_initial,
                optional_initial,
                _decoded_initial,
            ) = d.draw(seq_values_strategy(seq_klass=klass))
            obj_initial = klass(
                value_initial,
                schema_initial,
                impl_initial,
                expl_initial,
                default_initial,
                optional_initial or False,
                _decoded_initial,
            )
            (
                value,
                _,
                impl,
                expl,
                default,
                optional,
                _decoded,
            ) = d.draw(seq_values_strategy(
                seq_klass=klass,
                do_expl=impl_initial is None,
            ))
            obj = obj_initial(value, impl, expl, default, optional)
            value_expected = default if value is None else value
            value_expected = (
                default_initial if value_expected is None
                else value_expected
            )
            self.assertEqual(obj._value, getattr(value_expected, "_value", {}))
            self.assertEqual(obj.tag, impl or impl_initial or obj.tag_default)
            self.assertEqual(obj.expl_tag, expl or expl_initial)
            self.assertEqual(
                {} if obj.default is None else obj.default._value,
                getattr(default_initial if default is None else default, "_value", {}),
            )
            if obj.default is None:
                optional = optional_initial if optional is None else optional
                optional = False if optional is None else optional
            else:
                optional = True
            self.assertEqual(list(obj.specs.items()), schema_initial or [])
            self.assertEqual(obj.optional, optional)

    @given(data_strategy())
    def test_copy(self, d):
        class SeqInherited(self.base_klass):
            pass
        for klass in (self.base_klass, SeqInherited):
            values = d.draw(seq_values_strategy(seq_klass=klass))
            obj = klass(*values)
            obj_copied = obj.copy()
            self.assert_copied_basic_fields(obj, obj_copied)
            self.assertEqual(obj.specs, obj_copied.specs)
            self.assertEqual(obj._value, obj_copied._value)

    @given(data_strategy())
    def test_stripped(self, d):
        value = d.draw(integers())
        tag_impl = tag_encode(d.draw(integers(min_value=1)))

        class Seq(self.base_klass):
            impl = tag_impl
            schema = (("whatever", Integer()),)
        seq = Seq()
        seq["whatever"] = Integer(value)
        with self.assertRaises(NotEnoughData):
            seq.decode(seq.encode()[:-1])

    @given(data_strategy())
    def test_stripped_expl(self, d):
        value = d.draw(integers())
        tag_expl = tag_ctxc(d.draw(integers(min_value=1)))

        class Seq(self.base_klass):
            expl = tag_expl
            schema = (("whatever", Integer()),)
        seq = Seq()
        seq["whatever"] = Integer(value)
        with self.assertRaises(NotEnoughData):
            seq.decode(seq.encode()[:-1])

    @given(binary(min_size=2))
    def test_non_tag_mismatch_raised(self, junk):
        try:
            _, _, len_encoded = tag_strip(memoryview(junk))
            len_decode(len_encoded)
        except Exception:
            assume(True)
        else:
            assume(False)

        class Seq(self.base_klass):
            schema = (
                ("whatever", Integer()),
                ("junk", Any()),
                ("whenever", Integer()),
            )
        seq = Seq()
        seq["whatever"] = Integer(123)
        seq["junk"] = Any(junk)
        seq["whenever"] = Integer(123)
        with self.assertRaises(DecodeError):
            seq.decode(seq.encode())

    @given(
        integers(min_value=31),
        integers(min_value=0),
        lists(integers()),
    )
    def test_bad_tag(self, tag, offset, decode_path):
        decode_path = tuple(str(i) for i in decode_path)
        with self.assertRaises(DecodeError) as err:
            self.base_klass().decode(
                tag_encode(tag)[:-1],
                offset=offset,
                decode_path=decode_path,
            )
        repr(err.exception)
        self.assertEqual(err.exception.offset, offset)
        self.assertEqual(err.exception.decode_path, decode_path)

    @given(
        integers(min_value=128),
        integers(min_value=0),
        lists(integers()),
    )
    def test_bad_len(self, l, offset, decode_path):
        decode_path = tuple(str(i) for i in decode_path)
        with self.assertRaises(DecodeError) as err:
            self.base_klass().decode(
                self.base_klass.tag_default + len_encode(l)[:-1],
                offset=offset,
                decode_path=decode_path,
            )
        repr(err.exception)
        self.assertEqual(err.exception.offset, offset)
        self.assertEqual(err.exception.decode_path, decode_path)

    def _assert_expects(self, seq, expects):
        for expect in expects:
            self.assertEqual(
                seq.specs[expect["name"]].optional,
                expect["optional"],
            )
            if expect["default_value"] is not None:
                self.assertEqual(
                    seq.specs[expect["name"]].default,
                    expect["default_value"],
                )
            if expect["presented"]:
                self.assertIn(expect["name"], seq)
                self.assertEqual(seq[expect["name"]], expect["value"])

    @settings(max_examples=LONG_TEST_MAX_EXAMPLES)
    @given(data_strategy())
    def test_symmetric(self, d):
        seq, expects = d.draw(sequence_strategy(seq_klass=self.base_klass))
        self.assertTrue(seq.ready)
        self.assertFalse(seq.decoded)
        self._assert_expects(seq, expects)
        repr(seq)
        pprint(seq)
        seq_encoded = seq.encode()
        seq_decoded, tail = seq.decode(seq_encoded)
        self.assertEqual(tail, b"")
        self.assertTrue(seq.ready)
        self._assert_expects(seq_decoded, expects)
        self.assertEqual(seq, seq_decoded)
        self.assertEqual(seq_decoded.encode(), seq_encoded)
        for expect in expects:
            if not expect["presented"]:
                self.assertNotIn(expect["name"], seq_decoded)
                continue
            self.assertIn(expect["name"], seq_decoded)
            obj = seq_decoded[expect["name"]]
            self.assertTrue(obj.decoded)
            offset = obj.expl_offset if obj.expled else obj.offset
            tlvlen = obj.expl_tlvlen if obj.expled else obj.tlvlen
            self.assertSequenceEqual(
                seq_encoded[offset:offset + tlvlen],
                obj.encode(),
            )

    @settings(max_examples=LONG_TEST_MAX_EXAMPLES)
    @given(data_strategy())
    def test_symmetric_with_seq(self, d):
        seq, expect_outers = d.draw(sequences_strategy(seq_klass=self.base_klass))
        self.assertTrue(seq.ready)
        seq_encoded = seq.encode()
        seq_decoded, tail = seq.decode(seq_encoded)
        self.assertEqual(tail, b"")
        self.assertTrue(seq.ready)
        self.assertEqual(seq, seq_decoded)
        self.assertEqual(seq_decoded.encode(), seq_encoded)
        for expect_outer in expect_outers:
            if not expect_outer["presented"]:
                self.assertNotIn(expect_outer["name"], seq_decoded)
                continue
            self.assertIn(expect_outer["name"], seq_decoded)
            obj = seq_decoded[expect_outer["name"]]
            self.assertTrue(obj.decoded)
            offset = obj.expl_offset if obj.expled else obj.offset
            tlvlen = obj.expl_tlvlen if obj.expled else obj.tlvlen
            self.assertSequenceEqual(
                seq_encoded[offset:offset + tlvlen],
                obj.encode(),
            )
            self._assert_expects(obj, expect_outer["expects"])

    @given(data_strategy())
    def test_default_disappears(self, d):
        _schema = list(d.draw(dictionaries(
            text_letters(),
            sets(integers(), min_size=2, max_size=2),
            min_size=1,
        )).items())

        class Seq(self.base_klass):
            schema = [
                (n, Integer(default=d))
                for n, (_, d) in _schema
            ]
        seq = Seq()
        for name, (value, _) in _schema:
            seq[name] = Integer(value)
        self.assertEqual(len(seq._value), len(_schema))
        empty_seq = b"".join((self.base_klass.tag_default, len_encode(0)))
        self.assertGreater(len(seq.encode()), len(empty_seq))
        for name, (_, default) in _schema:
            seq[name] = Integer(default)
        self.assertEqual(len(seq._value), 0)
        self.assertSequenceEqual(seq.encode(), empty_seq)

    @given(data_strategy())
    def test_encoded_default_accepted(self, d):
        _schema = list(d.draw(dictionaries(
            text_letters(),
            integers(),
            min_size=1,
        )).items())
        tags = [tag_encode(tag) for tag in d.draw(sets(
            integers(min_value=0),
            min_size=len(_schema),
            max_size=len(_schema),
        ))]

        class SeqWithoutDefault(self.base_klass):
            schema = [
                (n, Integer(impl=t))
                for (n, _), t in zip(_schema, tags)
            ]
        seq_without_default = SeqWithoutDefault()
        for name, value in _schema:
            seq_without_default[name] = Integer(value)
        seq_encoded = seq_without_default.encode()

        class SeqWithDefault(self.base_klass):
            schema = [
                (n, Integer(default=v, impl=t))
                for (n, v), t in zip(_schema, tags)
            ]
        seq_with_default = SeqWithDefault()
        seq_decoded, _ = seq_with_default.decode(seq_encoded)
        for name, value in _schema:
            self.assertEqual(seq_decoded[name], seq_with_default[name])
            self.assertEqual(seq_decoded[name], value)

    @given(data_strategy())
    def test_missing_from_spec(self, d):
        names = list(d.draw(sets(text_letters(), min_size=2)))
        tags = [tag_encode(tag) for tag in d.draw(sets(
            integers(min_value=0),
            min_size=len(names),
            max_size=len(names),
        ))]
        names_tags = [(name, tag) for tag, name in sorted(zip(tags, names))]

        class SeqFull(self.base_klass):
            schema = [(n, Integer(impl=t)) for n, t in names_tags]
        seq_full = SeqFull()
        for i, name in enumerate(names):
            seq_full[name] = Integer(i)
        seq_encoded = seq_full.encode()
        altered = names_tags[:-2] + names_tags[-1:]

        class SeqMissing(self.base_klass):
            schema = [(n, Integer(impl=t)) for n, t in altered]
        seq_missing = SeqMissing()
        with self.assertRaises(TagMismatch):
            seq_missing.decode(seq_encoded)


class TestSequence(SeqMixing, CommonMixin, TestCase):
    base_klass = Sequence

    @given(
        integers(),
        binary(min_size=1),
    )
    def test_remaining(self, value, junk):
        class Seq(Sequence):
            schema = (
                ("whatever", Integer()),
            )
        int_encoded = Integer(value).encode()
        junked = b"".join((
            Sequence.tag_default,
            len_encode(len(int_encoded + junk)),
            int_encoded + junk,
        ))
        with assertRaisesRegex(self, DecodeError, "remaining"):
            Seq().decode(junked)

    @given(sets(text_letters(), min_size=2))
    def test_obj_unknown(self, names):
        missing = names.pop()

        class Seq(Sequence):
            schema = [(n, Boolean()) for n in names]
        seq = Seq()
        with self.assertRaises(ObjUnknown) as err:
            seq[missing]
        repr(err.exception)
        with self.assertRaises(ObjUnknown) as err:
            seq[missing] = Boolean()
        repr(err.exception)


class TestSet(SeqMixing, CommonMixin, TestCase):
    base_klass = Set

    @settings(max_examples=LONG_TEST_MAX_EXAMPLES)
    @given(data_strategy())
    def test_sorted(self, d):
        tags = [
            tag_encode(tag) for tag in
            d.draw(sets(integers(min_value=1), min_size=1, max_size=10))
        ]

        class Seq(Set):
            schema = [(str(i), OctetString(impl=t)) for i, t in enumerate(tags)]
        seq = Seq()
        for name, _ in Seq.schema:
            seq[name] = OctetString(b"")
        seq_encoded = seq.encode()
        seq_decoded, _ = seq.decode(seq_encoded)
        self.assertSequenceEqual(
            seq_encoded[seq_decoded.tlen + seq_decoded.llen:],
            b"".join(sorted([seq[name].encode() for name, _ in Seq.schema])),
        )


@composite
def seqof_values_strategy(draw, schema=None, do_expl=False):
    if schema is None:
        schema = draw(sampled_from((Boolean(), Integer())))
    bound_min, bound_max = sorted(draw(sets(
        integers(min_value=0, max_value=10),
        min_size=2,
        max_size=2,
    )))
    if isinstance(schema, Boolean):
        values_generator = booleans().map(Boolean)
    elif isinstance(schema, Integer):
        values_generator = integers().map(Integer)
    values_generator = lists(
        values_generator,
        min_size=bound_min,
        max_size=bound_max,
    )
    values = draw(one_of(none(), values_generator))
    impl = None
    expl = None
    if do_expl:
        expl = draw(one_of(none(), integers(min_value=1).map(tag_encode)))
    else:
        impl = draw(one_of(none(), integers(min_value=1).map(tag_encode)))
    default = draw(one_of(none(), values_generator))
    optional = draw(one_of(none(), booleans()))
    _decoded = (
        draw(integers(min_value=0)),
        draw(integers(min_value=0)),
        draw(integers(min_value=0)),
    )
    return (
        schema,
        values,
        (bound_min, bound_max),
        impl,
        expl,
        default,
        optional,
        _decoded,
    )


class SeqOfMixing(object):
    def test_invalid_value_type(self):
        with self.assertRaises(InvalidValueType) as err:
            self.base_klass(123)
        repr(err.exception)

    def test_invalid_values_type(self):
        class SeqOf(self.base_klass):
            schema = Integer()
        with self.assertRaises(InvalidValueType) as err:
            SeqOf([Integer(123), Boolean(False), Integer(234)])
        repr(err.exception)

    def test_schema_required(self):
        with assertRaisesRegex(self, ValueError, "schema must be specified"):
            self.base_klass.__mro__[1]()

    @given(booleans(), booleans(), binary(), binary())
    def test_comparison(self, value1, value2, tag1, tag2):
        class SeqOf(self.base_klass):
            schema = Boolean()
        obj1 = SeqOf([Boolean(value1)])
        obj2 = SeqOf([Boolean(value2)])
        self.assertEqual(obj1 == obj2, value1 == value2)
        self.assertEqual(obj1 != obj2, value1 != value2)
        self.assertEqual(obj1 == list(obj2), value1 == value2)
        self.assertEqual(obj1 == tuple(obj2), value1 == value2)
        obj1 = SeqOf([Boolean(value1)], impl=tag1)
        obj2 = SeqOf([Boolean(value1)], impl=tag2)
        self.assertEqual(obj1 == obj2, tag1 == tag2)
        self.assertEqual(obj1 != obj2, tag1 != tag2)

    @given(lists(booleans()))
    def test_iter(self, values):
        class SeqOf(self.base_klass):
            schema = Boolean()
        obj = SeqOf([Boolean(value) for value in values])
        self.assertEqual(len(obj), len(values))
        for i, value in enumerate(obj):
            self.assertEqual(value, values[i])

    @given(data_strategy())
    def test_ready(self, d):
        ready = [Integer(v) for v in d.draw(lists(
            integers(),
            min_size=1,
            max_size=3,
        ))]
        non_ready = [
            Integer() for _ in
            range(d.draw(integers(min_value=1, max_value=5)))
        ]

        class SeqOf(self.base_klass):
            schema = Integer()
        values = d.draw(permutations(ready + non_ready))
        seqof = SeqOf()
        for value in values:
            seqof.append(value)
        self.assertFalse(seqof.ready)
        repr(seqof)
        pprint(seqof)
        with self.assertRaises(ObjNotReady) as err:
            seqof.encode()
        repr(err.exception)
        for i, value in enumerate(values):
            self.assertEqual(seqof[i], value)
            if not seqof[i].ready:
                seqof[i] = Integer(i)
        self.assertTrue(seqof.ready)
        repr(seqof)
        pprint(seqof)

    def test_spec_mismatch(self):
        class SeqOf(self.base_klass):
            schema = Integer()
        seqof = SeqOf()
        seqof.append(Integer(123))
        with self.assertRaises(ValueError):
            seqof.append(Boolean(False))
        with self.assertRaises(ValueError):
            seqof[0] = Boolean(False)

    @given(data_strategy())
    def test_bounds_satisfied(self, d):
        class SeqOf(self.base_klass):
            schema = Boolean()
        bound_min = d.draw(integers(min_value=0, max_value=1 << 7))
        bound_max = d.draw(integers(min_value=bound_min, max_value=1 << 7))
        value = [Boolean()] * d.draw(integers(min_value=bound_min, max_value=bound_max))
        SeqOf(value=value, bounds=(bound_min, bound_max))

    @given(data_strategy())
    def test_bounds_unsatisfied(self, d):
        class SeqOf(self.base_klass):
            schema = Boolean()
        bound_min = d.draw(integers(min_value=1, max_value=1 << 7))
        bound_max = d.draw(integers(min_value=bound_min, max_value=1 << 7))
        value = [Boolean()] * d.draw(integers(max_value=bound_min - 1))
        with self.assertRaises(BoundsError) as err:
            SeqOf(value=value, bounds=(bound_min, bound_max))
        repr(err.exception)
        value = [Boolean()] * d.draw(integers(
            min_value=bound_max + 1,
            max_value=bound_max + 10,
        ))
        with self.assertRaises(BoundsError) as err:
            SeqOf(value=value, bounds=(bound_min, bound_max))
        repr(err.exception)

    @given(integers(min_value=1, max_value=10))
    def test_out_of_bounds(self, bound_max):
        class SeqOf(self.base_klass):
            schema = Integer()
            bounds = (0, bound_max)
        seqof = SeqOf()
        for _ in range(bound_max):
            seqof.append(Integer(123))
        with self.assertRaises(BoundsError):
            seqof.append(Integer(123))

    @given(data_strategy())
    def test_call(self, d):
        (
            schema_initial,
            value_initial,
            bounds_initial,
            impl_initial,
            expl_initial,
            default_initial,
            optional_initial,
            _decoded_initial,
        ) = d.draw(seqof_values_strategy())

        class SeqOf(self.base_klass):
            schema = schema_initial
        obj_initial = SeqOf(
            value=value_initial,
            bounds=bounds_initial,
            impl=impl_initial,
            expl=expl_initial,
            default=default_initial,
            optional=optional_initial or False,
            _decoded=_decoded_initial,
        )
        (
            _,
            value,
            bounds,
            impl,
            expl,
            default,
            optional,
            _decoded,
        ) = d.draw(seqof_values_strategy(
            schema=schema_initial,
            do_expl=impl_initial is None,
        ))
        if (default is None) and (obj_initial.default is not None):
            bounds = None
        if (
                (bounds is None) and
                (value is not None) and
                (bounds_initial is not None) and
                not (bounds_initial[0] <= len(value) <= bounds_initial[1])
        ):
            value = None
        if (
                (bounds is None) and
                (default is not None) and
                (bounds_initial is not None) and
                not (bounds_initial[0] <= len(default) <= bounds_initial[1])
        ):
            default = None
        obj = obj_initial(
            value=value,
            bounds=bounds,
            impl=impl,
            expl=expl,
            default=default,
            optional=optional,
        )
        if obj.ready:
            value_expected = default if value is None else value
            value_expected = (
                default_initial if value_expected is None
                else value_expected
            )
            value_expected = () if value_expected is None else value_expected
            self.assertEqual(obj, value_expected)
        self.assertEqual(obj.tag, impl or impl_initial or obj.tag_default)
        self.assertEqual(obj.expl_tag, expl or expl_initial)
        self.assertEqual(
            obj.default,
            default_initial if default is None else default,
        )
        if obj.default is None:
            optional = optional_initial if optional is None else optional
            optional = False if optional is None else optional
        else:
            optional = True
        self.assertEqual(obj.optional, optional)
        self.assertEqual(
            (obj._bound_min, obj._bound_max),
            bounds or bounds_initial or (0, float("+inf")),
        )

    @given(seqof_values_strategy())
    def test_copy(self, values):
        _schema, value, bounds, impl, expl, default, optional, _decoded = values

        class SeqOf(self.base_klass):
            schema = _schema
        obj = SeqOf(
            value=value,
            bounds=bounds,
            impl=impl,
            expl=expl,
            default=default,
            optional=optional or False,
            _decoded=_decoded,
        )
        obj_copied = obj.copy()
        self.assert_copied_basic_fields(obj, obj_copied)
        self.assertEqual(obj._bound_min, obj_copied._bound_min)
        self.assertEqual(obj._bound_max, obj_copied._bound_max)
        self.assertEqual(obj._value, obj_copied._value)

    @given(
        lists(binary()),
        integers(min_value=1).map(tag_encode),
    )
    def test_stripped(self, values, tag_impl):
        class SeqOf(self.base_klass):
            schema = OctetString()
        obj = SeqOf([OctetString(v) for v in values], impl=tag_impl)
        with self.assertRaises(NotEnoughData):
            obj.decode(obj.encode()[:-1])

    @given(
        lists(binary()),
        integers(min_value=1).map(tag_ctxc),
    )
    def test_stripped_expl(self, values, tag_expl):
        class SeqOf(self.base_klass):
            schema = OctetString()
        obj = SeqOf([OctetString(v) for v in values], expl=tag_expl)
        with self.assertRaises(NotEnoughData):
            obj.decode(obj.encode()[:-1])

    @given(
        integers(min_value=31),
        integers(min_value=0),
        lists(integers()),
    )
    def test_bad_tag(self, tag, offset, decode_path):
        decode_path = tuple(str(i) for i in decode_path)
        with self.assertRaises(DecodeError) as err:
            self.base_klass().decode(
                tag_encode(tag)[:-1],
                offset=offset,
                decode_path=decode_path,
            )
        repr(err.exception)
        self.assertEqual(err.exception.offset, offset)
        self.assertEqual(err.exception.decode_path, decode_path)

    @given(
        integers(min_value=128),
        integers(min_value=0),
        lists(integers()),
    )
    def test_bad_len(self, l, offset, decode_path):
        decode_path = tuple(str(i) for i in decode_path)
        with self.assertRaises(DecodeError) as err:
            self.base_klass().decode(
                self.base_klass.tag_default + len_encode(l)[:-1],
                offset=offset,
                decode_path=decode_path,
            )
        repr(err.exception)
        self.assertEqual(err.exception.offset, offset)
        self.assertEqual(err.exception.decode_path, decode_path)

    @given(binary(min_size=1))
    def test_tag_mismatch(self, impl):
        assume(impl != self.base_klass.tag_default)
        with self.assertRaises(TagMismatch):
            self.base_klass(impl=impl).decode(self.base_klass().encode())

    @settings(max_examples=LONG_TEST_MAX_EXAMPLES)
    @given(
        seqof_values_strategy(schema=Integer()),
        lists(integers().map(Integer)),
        integers(min_value=1).map(tag_ctxc),
        integers(min_value=0),
    )
    def test_symmetric(self, values, value, tag_expl, offset):
        _, _, _, _, _, default, optional, _decoded = values

        class SeqOf(self.base_klass):
            schema = Integer()
        obj = SeqOf(
            value=value,
            default=default,
            optional=optional,
            _decoded=_decoded,
        )
        repr(obj)
        pprint(obj)
        self.assertFalse(obj.expled)
        obj_encoded = obj.encode()
        obj_expled = obj(value, expl=tag_expl)
        self.assertTrue(obj_expled.expled)
        repr(obj_expled)
        pprint(obj_expled)
        obj_expled_encoded = obj_expled.encode()
        obj_decoded, tail = obj_expled.decode(obj_expled_encoded, offset=offset)
        repr(obj_decoded)
        pprint(obj_decoded)
        self.assertEqual(tail, b"")
        self._test_symmetric_compare_objs(obj_decoded, obj_expled)
        self.assertSequenceEqual(obj_decoded.encode(), obj_expled_encoded)
        self.assertSequenceEqual(obj_decoded.expl_tag, tag_expl)
        self.assertEqual(obj_decoded.expl_tlen, len(tag_expl))
        self.assertEqual(
            obj_decoded.expl_llen,
            len(len_encode(len(obj_encoded))),
        )
        self.assertEqual(obj_decoded.tlvlen, len(obj_encoded))
        self.assertEqual(obj_decoded.expl_vlen, len(obj_encoded))
        self.assertEqual(
            obj_decoded.offset,
            offset + obj_decoded.expl_tlen + obj_decoded.expl_llen,
        )
        self.assertEqual(obj_decoded.expl_offset, offset)
        for obj_inner in obj_decoded:
            self.assertIn(obj_inner, obj_decoded)
            self.assertSequenceEqual(
                obj_inner.encode(),
                obj_expled_encoded[
                    obj_inner.offset - offset:
                    obj_inner.offset + obj_inner.tlvlen - offset
                ],
            )


class TestSequenceOf(SeqOfMixing, CommonMixin, TestCase):
    class SeqOf(SequenceOf):
        schema = "whatever"
    base_klass = SeqOf

    def _test_symmetric_compare_objs(self, obj1, obj2):
        self.assertEqual(obj1, obj2)
        self.assertSequenceEqual(list(obj1), list(obj2))


class TestSetOf(SeqOfMixing, CommonMixin, TestCase):
    class SeqOf(SetOf):
        schema = "whatever"
    base_klass = SeqOf

    def _test_symmetric_compare_objs(self, obj1, obj2):
        self.assertSetEqual(
            set(int(v) for v in obj1),
            set(int(v) for v in obj2),
        )

    @settings(max_examples=LONG_TEST_MAX_EXAMPLES)
    @given(data_strategy())
    def test_sorted(self, d):
        values = [OctetString(v) for v in d.draw(lists(binary()))]

        class Seq(SetOf):
            schema = OctetString()
        seq = Seq(values)
        seq_encoded = seq.encode()
        seq_decoded, _ = seq.decode(seq_encoded)
        self.assertSequenceEqual(
            seq_encoded[seq_decoded.tlen + seq_decoded.llen:],
            b"".join(sorted([v.encode() for v in values])),
        )


class TestGoMarshalVectors(TestCase):
    def runTest(self):
        self.assertSequenceEqual(Integer(10).encode(), hexdec("02010a"))
        self.assertSequenceEqual(Integer(127).encode(), hexdec("02017f"))
        self.assertSequenceEqual(Integer(128).encode(), hexdec("02020080"))
        self.assertSequenceEqual(Integer(-128).encode(), hexdec("020180"))
        self.assertSequenceEqual(Integer(-129).encode(), hexdec("0202ff7f"))

        class Seq(Sequence):
            schema = (
                ("erste", Integer()),
                ("zweite", Integer(optional=True))
            )
        seq = Seq()
        seq["erste"] = Integer(64)
        self.assertSequenceEqual(seq.encode(), hexdec("3003020140"))
        seq["erste"] = Integer(0x123456)
        self.assertSequenceEqual(seq.encode(), hexdec("30050203123456"))
        seq["erste"] = Integer(64)
        seq["zweite"] = Integer(65)
        self.assertSequenceEqual(seq.encode(), hexdec("3006020140020141"))

        class NestedSeq(Sequence):
            schema = (
                ("nest", Seq()),
            )
        seq["erste"] = Integer(127)
        seq["zweite"] = None
        nested = NestedSeq()
        nested["nest"] = seq
        self.assertSequenceEqual(nested.encode(), hexdec("3005300302017f"))

        self.assertSequenceEqual(
            OctetString(b"\x01\x02\x03").encode(),
            hexdec("0403010203"),
        )

        class Seq(Sequence):
            schema = (
                ("erste", Integer(impl=tag_encode(5, klass=TagClassContext))),
            )
        seq = Seq()
        seq["erste"] = Integer(64)
        self.assertSequenceEqual(seq.encode(), hexdec("3003850140"))

        class Seq(Sequence):
            schema = (
                ("erste", Integer(expl=tag_ctxc(5))),
            )
        seq = Seq()
        seq["erste"] = Integer(64)
        self.assertSequenceEqual(seq.encode(), hexdec("3005a503020140"))

        class Seq(Sequence):
            schema = (
                ("erste", Null(
                    impl=tag_encode(0, klass=TagClassContext),
                    optional=True,
                )),
            )
        seq = Seq()
        seq["erste"] = Null()
        self.assertSequenceEqual(seq.encode(), hexdec("30028000"))
        seq["erste"] = None
        self.assertSequenceEqual(seq.encode(), hexdec("3000"))

        self.assertSequenceEqual(
            UTCTime(datetime(1970, 1, 1, 0, 0)).encode(),
            hexdec("170d3730303130313030303030305a"),
        )
        self.assertSequenceEqual(
            UTCTime(datetime(2009, 11, 15, 22, 56, 16)).encode(),
            hexdec("170d3039313131353232353631365a"),
        )
        self.assertSequenceEqual(
            GeneralizedTime(datetime(2100, 4, 5, 12, 1, 1)).encode(),
            hexdec("180f32313030303430353132303130315a"),
        )

        class Seq(Sequence):
            schema = (
                ("erste", GeneralizedTime()),
            )
        seq = Seq()
        seq["erste"] = GeneralizedTime(datetime(2009, 11, 15, 22, 56, 16))
        self.assertSequenceEqual(
            seq.encode(),
            hexdec("3011180f32303039313131353232353631365a"),
        )

        self.assertSequenceEqual(
            BitString((1, b"\x80")).encode(),
            hexdec("03020780"),
        )
        self.assertSequenceEqual(
            BitString((12, b"\x81\xF0")).encode(),
            hexdec("03030481f0"),
        )

        self.assertSequenceEqual(
            ObjectIdentifier("1.2.3.4").encode(),
            hexdec("06032a0304"),
        )
        self.assertSequenceEqual(
            ObjectIdentifier("1.2.840.133549.1.1.5").encode(),
            hexdec("06092a864888932d010105"),
        )
        self.assertSequenceEqual(
            ObjectIdentifier("2.100.3").encode(),
            hexdec("0603813403"),
        )

        self.assertSequenceEqual(
            PrintableString("test").encode(),
            hexdec("130474657374"),
        )
        self.assertSequenceEqual(
            PrintableString("x" * 127).encode(),
            hexdec("137F" + "78" * 127),
        )
        self.assertSequenceEqual(
            PrintableString("x" * 128).encode(),
            hexdec("138180" + "78" * 128),
        )
        self.assertSequenceEqual(UTF8String("Σ").encode(), hexdec("0c02cea3"))

        class Seq(Sequence):
            schema = (
                ("erste", IA5String()),
            )
        seq = Seq()
        seq["erste"] = IA5String("test")
        self.assertSequenceEqual(seq.encode(), hexdec("3006160474657374"))

        class Seq(Sequence):
            schema = (
                ("erste", PrintableString()),
            )
        seq = Seq()
        seq["erste"] = PrintableString("test")
        self.assertSequenceEqual(seq.encode(), hexdec("3006130474657374"))
        seq["erste"] = PrintableString("test*")
        self.assertSequenceEqual(seq.encode(), hexdec("30071305746573742a"))

        class Seq(Sequence):
            schema = (
                ("erste", Any(optional=True)),
                ("zweite", Integer()),
            )
        seq = Seq()
        seq["zweite"] = Integer(64)
        self.assertSequenceEqual(seq.encode(), hexdec("3003020140"))

        class Seq(SetOf):
            schema = Integer()
        seq = Seq()
        seq.append(Integer(10))
        self.assertSequenceEqual(seq.encode(), hexdec("310302010a"))

        class _SeqOf(SequenceOf):
            schema = PrintableString()

        class SeqOf(SequenceOf):
            schema = _SeqOf()
        _seqof = _SeqOf()
        _seqof.append(PrintableString("1"))
        seqof = SeqOf()
        seqof.append(_seqof)
        self.assertSequenceEqual(seqof.encode(), hexdec("30053003130131"))

        class Seq(Sequence):
            schema = (
                ("erste", Integer(default=1)),
            )
        seq = Seq()
        seq["erste"] = Integer(0)
        self.assertSequenceEqual(seq.encode(), hexdec("3003020100"))
        seq["erste"] = Integer(1)
        self.assertSequenceEqual(seq.encode(), hexdec("3000"))
        seq["erste"] = Integer(2)
        self.assertSequenceEqual(seq.encode(), hexdec("3003020102"))


class TestPP(TestCase):
    @given(data_strategy())
    def test_oid_printing(self, d):
        oids = {
            str(ObjectIdentifier(k)): v * 2
            for k, v in d.draw(dictionaries(oid_strategy(), text_letters())).items()
        }
        chosen = d.draw(sampled_from(sorted(oids)))
        chosen_id = oids[chosen]
        pp = _pp(asn1_type_name=ObjectIdentifier.asn1_type_name, value=chosen)
        self.assertNotIn(chosen_id, pp_console_row(pp))
        self.assertIn(chosen_id, pp_console_row(pp, oids=oids))


class TestAutoAddSlots(TestCase):
    def runTest(self):
        class Inher(Integer):
            pass

        with self.assertRaises(AttributeError):
            inher = Inher()
            inher.unexistent = "whatever"


class TestOIDDefines(TestCase):
    @given(data_strategy())
    def runTest(self, d):
        value_names = list(d.draw(sets(text_letters(), min_size=1, max_size=10)))
        value_name_chosen = d.draw(sampled_from(value_names))
        oids = [
            ObjectIdentifier(oid)
            for oid in d.draw(sets(oid_strategy(), min_size=2, max_size=10))
        ]
        oid_chosen = d.draw(sampled_from(oids))
        values = d.draw(lists(
            integers(),
            min_size=len(value_names),
            max_size=len(value_names),
        ))
        _schema = [
            ("type", ObjectIdentifier(defines=(value_name_chosen, {
                oid: Integer() for oid in oids[:-1]
            }))),
        ]
        for i, value_name in enumerate(value_names):
            _schema.append((value_name, Any(expl=tag_ctxp(i))))

        class Seq(Sequence):
            schema = _schema
        seq = Seq()
        for value_name, value in zip(value_names, values):
            seq[value_name] = Any(Integer(value).encode())
        seq["type"] = oid_chosen
        seq, _ = Seq().decode(seq.encode())
        for value_name in value_names:
            if value_name == value_name_chosen:
                continue
            self.assertIsNone(seq[value_name].defined)
        if value_name_chosen in oids[:-1]:
            self.assertIsNotNone(seq[value_name_chosen].defined)
            self.assertEqual(seq[value_name_chosen].defined[0], oid_chosen)
            self.assertIsInstance(seq[value_name_chosen].defined[1], Integer)


class TestDefinesByPath(TestCase):
    def runTest(self):
        class Seq(Sequence):
            schema = (
                ("type", ObjectIdentifier()),
                ("value", OctetString(expl=tag_ctxc(123))),
            )

        class SeqInner(Sequence):
            schema = (
                ("typeInner", ObjectIdentifier()),
                ("valueInner", Any()),
            )

        class PairValue(SetOf):
            schema = Any()

        class Pair(Sequence):
            schema = (
                ("type", ObjectIdentifier()),
                ("value", PairValue()),
            )

        class Pairs(SequenceOf):
            schema = Pair()

        (
            type_integered,
            type_sequenced,
            type_innered,
            type_octet_stringed,
        ) = [
            ObjectIdentifier(oid)
            for oid in sets(oid_strategy(), min_size=4, max_size=4).example()
        ]
        seq_integered = Seq()
        seq_integered["type"] = type_integered
        seq_integered["value"] = OctetString(Integer(123).encode())
        seq_integered_raw = seq_integered.encode()

        pairs = Pairs()
        pairs_input = (
            (type_octet_stringed, OctetString(b"whatever")),
            (type_integered, Integer(123)),
            (type_octet_stringed, OctetString(b"whenever")),
            (type_integered, Integer(234)),
        )
        for t, v in pairs_input:
            pair = Pair()
            pair["type"] = t
            pair["value"] = PairValue((Any(v),))
            pairs.append(pair)
        seq_inner = SeqInner()
        seq_inner["typeInner"] = type_innered
        seq_inner["valueInner"] = Any(pairs)
        seq_sequenced = Seq()
        seq_sequenced["type"] = type_sequenced
        seq_sequenced["value"] = OctetString(seq_inner.encode())
        seq_sequenced_raw = seq_sequenced.encode()

        defines_by_path = []
        seq_integered, _ = Seq().decode(seq_integered_raw)
        self.assertIsNone(seq_integered["value"].defined)
        defines_by_path.append(
            (("type",), ("value", {
                type_integered: Integer(),
                type_sequenced: SeqInner(),
            }))
        )
        seq_integered, _ = Seq().decode(seq_integered_raw, defines_by_path=defines_by_path)
        self.assertIsNotNone(seq_integered["value"].defined)
        self.assertEqual(seq_integered["value"].defined[0], type_integered)
        self.assertEqual(seq_integered["value"].defined[1], Integer(123))

        seq_sequenced, _ = Seq().decode(seq_sequenced_raw, defines_by_path=defines_by_path)
        self.assertIsNotNone(seq_sequenced["value"].defined)
        self.assertEqual(seq_sequenced["value"].defined[0], type_sequenced)
        seq_inner = seq_sequenced["value"].defined[1]
        self.assertIsNone(seq_inner["valueInner"].defined)

        defines_by_path.append((
            ("value", decode_path_defby(type_sequenced), "typeInner"),
            ("valueInner", {type_innered: Pairs()}),
        ))
        seq_sequenced, _ = Seq().decode(seq_sequenced_raw, defines_by_path=defines_by_path)
        self.assertIsNotNone(seq_sequenced["value"].defined)
        self.assertEqual(seq_sequenced["value"].defined[0], type_sequenced)
        seq_inner = seq_sequenced["value"].defined[1]
        self.assertIsNotNone(seq_inner["valueInner"].defined)
        self.assertEqual(seq_inner["valueInner"].defined[0], type_innered)
        pairs = seq_inner["valueInner"].defined[1]
        for pair in pairs:
            self.assertIsNone(pair["value"][0].defined)

        defines_by_path.append((
            (
                "value",
                decode_path_defby(type_sequenced),
                "valueInner",
                decode_path_defby(type_innered),
                any,
                "type",
            ),
            ("value", {
                type_integered: Integer(),
                type_octet_stringed: OctetString(),
            }),
        ))
        seq_sequenced, _ = Seq().decode(seq_sequenced_raw, defines_by_path=defines_by_path)
        self.assertIsNotNone(seq_sequenced["value"].defined)
        self.assertEqual(seq_sequenced["value"].defined[0], type_sequenced)
        seq_inner = seq_sequenced["value"].defined[1]
        self.assertIsNotNone(seq_inner["valueInner"].defined)
        self.assertEqual(seq_inner["valueInner"].defined[0], type_innered)
        pairs_got = seq_inner["valueInner"].defined[1]
        for pair_input, pair_got in zip(pairs_input, pairs_got):
            self.assertEqual(pair_got["value"][0].defined[0], pair_input[0])
            self.assertEqual(pair_got["value"][0].defined[1], pair_input[1])
