#!/usr/bin/env python
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
"""Python ASN.1 DER codec with abstract structures

This library allows you to marshal and unmarshal various structures in
ASN.1 DER format, like this:

    >>> i = Integer(123)
    >>> raw = i.encode()
    >>> Integer().decode(raw) == i
    True

There are primitive types, holding single values
(:py:class:`pyderasn.BitString`,
:py:class:`pyderasn.Boolean`,
:py:class:`pyderasn.Enumerated`,
:py:class:`pyderasn.GeneralizedTime`,
:py:class:`pyderasn.Integer`,
:py:class:`pyderasn.Null`,
:py:class:`pyderasn.ObjectIdentifier`,
:py:class:`pyderasn.OctetString`,
:py:class:`pyderasn.UTCTime`,
:py:class:`various strings <pyderasn.CommonString>`
(:py:class:`pyderasn.BMPString`,
:py:class:`pyderasn.GeneralString`,
:py:class:`pyderasn.GraphicString`,
:py:class:`pyderasn.IA5String`,
:py:class:`pyderasn.ISO646String`,
:py:class:`pyderasn.NumericString`,
:py:class:`pyderasn.PrintableString`,
:py:class:`pyderasn.T61String`,
:py:class:`pyderasn.TeletexString`,
:py:class:`pyderasn.UniversalString`,
:py:class:`pyderasn.UTF8String`,
:py:class:`pyderasn.VideotexString`,
:py:class:`pyderasn.VisibleString`)),
constructed types, holding multiple primitive types
(:py:class:`pyderasn.Sequence`,
:py:class:`pyderasn.SequenceOf`,
:py:class:`pyderasn.Set`,
:py:class:`pyderasn.SetOf`),
and special types like
:py:class:`pyderasn.Any` and
:py:class:`pyderasn.Choice`.

Common for most types
---------------------

Tags
____

Most types in ASN.1 has specific tag for them. ``Obj.tag_default`` is
the default tag used during coding process. You can override it with
either ``IMPLICIT`` (using ``impl`` keyword argument), or
``EXPLICIT`` one (using ``expl`` keyword argument). Both arguments takes
raw binary string, containing that tag. You can **not** set implicit and
explicit tags simultaneously.

There are :py:func:`pyderasn.tag_ctxp` and :py:func:`pyderasn.tag_ctxc`
functions, allowing you to easily create ``CONTEXT``
``PRIMITIVE``/``CONSTRUCTED`` tags, by specifying only the required tag
number. Pay attention that explicit tags always have *constructed* tag
(``tag_ctxc``), but implicit tags for primitive types are primitive
(``tag_ctxp``).

::

    >>> Integer(impl=tag_ctxp(1))
    [1] INTEGER
    >>> Integer(expl=tag_ctxc(2))
    [2] EXPLICIT INTEGER

Implicit tag is not explicitly shown.

Two object of the same type, but with different implicit/explicit tags
are **not** equal.

You can get objects effective tag (either default or implicited) through
``tag`` property. You can decode it using :py:func:`pyderasn.tag_decode`
function::

    >>> tag_decode(tag_ctxc(123))
    (128, 32, 123)
    >>> klass, form, num = tag_decode(tag_ctxc(123))
    >>> klass == TagClassContext
    True
    >>> form == TagFormConstructed
    True

To determine if object has explicit tag, use ``expled`` boolean property
and ``expl_tag`` property, returning explicit tag's value.

Default/optional
________________

Many objects in sequences could be ``OPTIONAL`` and could have
``DEFAULT`` value. You can specify that object's property using
corresponding keyword arguments.

    >>> Integer(optional=True, default=123)
    INTEGER 123 OPTIONAL DEFAULT

Those specifications do not play any role in primitive value encoding,
but are taken into account when dealing with sequences holding them. For
example ``TBSCertificate`` sequence holds defaulted, explicitly tagged
``version`` field::

    class Version(Integer):
        schema = (
            ("v1", 0),
            ("v2", 1),
            ("v3", 2),
        )
    class TBSCertificate(Sequence):
        schema = (
            ("version", Version(expl=tag_ctxc(0), default="v1")),
        [...]

When default argument is used and value is not specified, then it equals
to default one.

.. _bounds:

Size constraints
________________

Some objects give ability to set value size constraints. This is either
possible integer value, or allowed length of various strings and
sequences. Constraints are set in the following way::

    class X(...):
        bounds = (MIN, MAX)

And values satisfaction is checked as: ``MIN <= X <= MAX``.

For simplicity you can also set bounds the following way::

    bounded_x = X(bounds=(MIN, MAX))

If bounds are not satisfied, then :py:exc:`pyderasn.BoundsError` is
raised.

Common methods
______________

All objects have ``ready`` boolean property, that tells if it is ready
to be encoded. If that kind of action is performed on unready object,
then :py:exc:`pyderasn.ObjNotReady` exception will be raised.

All objects have ``copy()`` method, returning its copy, that can be safely
mutated.

.. _decoding:

Decoding
--------

Decoding is performed using ``decode()`` method. ``offset`` optional
argument could be used to set initial object's offset in the binary
data, for convenience. It returns decoded object and remaining
unmarshalled data (tail). Internally all work is done on
``memoryview(data)``, and you can leave returning tail as a memoryview,
by specifying ``leavemm=True`` argument.

When object is decoded, ``decoded`` property is true and you can safely
use following properties:

* ``offset`` -- position including initial offset where object's tag starts
* ``tlen`` -- length of object's tag
* ``llen`` -- length of object's length value
* ``vlen`` -- length of object's value
* ``tlvlen`` -- length of the whole object

Pay attention that those values do **not** include anything related to
explicit tag. If you want to know information about it, then use:
``expled`` (to know if explicit tag is set), ``expl_offset`` (it is
lesser than ``offset``), ``expl_tlen``, ``expl_llen``, ``expl_vlen``
(that actually equals to ordinary ``tlvlen``).

When error occurs, then :py:exc:`pyderasn.DecodeError` is raised.

.. _pprinting:

Pretty printing
---------------

All objects have ``pps()`` method, that is a generator of
:py:class:`pyderasn.PP` namedtuple, holding various raw information
about the object. If ``pps`` is called on sequences, then all underlying
``PP`` will be yielded.

You can use :py:func:`pyderasn.pp_console_row` function, converting
those ``PP`` to human readable string. Actually exactly it is used for
all object ``repr``. But it is easy to write custom formatters.

    >>> from pyderasn import pprint
    >>> encoded = Integer(-12345).encode()
    >>> obj, tail = Integer().decode(encoded)
    >>> print(pprint(obj))
        0   [1,1,   2] INTEGER -12345

.. _definedby:

DEFINED BY
----------

ASN.1 structures often have ANY and OCTET STRING fields, that are
DEFINED BY some previously met ObjectIdentifier. This library provides
ability to specify mapping between some OID and field that must be
decoded with specific specification.

defines kwarg
_____________

:py:class:`pyderasn.ObjectIdentifier` field inside
:py:class:`pyderasn.Sequence` can hold mapping between OIDs and
necessary for decoding structrures. For example, CMS (:rfc:`5652`)
container::

    class ContentInfo(Sequence):
        schema = (
            ("contentType", ContentType(defines=("content", {
                id_digestedData: DigestedData(),
                id_signedData: SignedData(),
            }))),
            ("content", Any(expl=tag_ctxc(0))),
        )

``contentType`` field tells that it defines that ``content`` must be
decoded with ``SignedData`` specification, if ``contentType`` equals to
``id-signedData``. The same applies to ``DigestedData``. If
``contentType`` contains unknown OID, then no automatic decoding is
done.

Following types can be automatically decoded (DEFINED BY):

* :py:class:`pyderasn.Any`
* :py:class:`pyderasn.OctetString`
* :py:class:`pyderasn.SequenceOf`/:py:class:`pyderasn.SetOf`
  ``Any``/``OctetString``-s

When any of those fields is automatically decoded, then ``.defined``
attribute contains ``(OID, value)`` tuple. OID tell by which OID it was
defined, ``value`` contains corresponding decoded value. For example
above, ``content_info["content"].defined == (id_signedData,
signed_data)``.

.. _defines_by_path_kwarg:

defines_by_path kwarg
_____________________

Sometimes you either can not or do not want to explicitly set *defines*
in the scheme. You can dynamically apply those definitions when calling
``.decode()`` method.

Decode method takes optional ``defines_by_path`` keyword argument that
must be sequence of following tuples::

    (decode_path, defines)

where ``decode_path`` is a tuple holding so-called decode path to the
exact :py:class:`pyderasn.ObjectIdentifier` field you want to apply
``defines``, holding exactly the same value as accepted in its keyword
argument.

For example, again for CMS, you want to automatically decode
``SignedData`` and CMC's (:rfc:`5272`) ``PKIData`` and ``PKIResponse``
structures it may hold. Also, automatically decode ``controlSequence``
of ``PKIResponse``::

    content_info, tail = ContentInfo().decode(data, defines_by_path=(
        (
            ("contentType",),
            ("content", {id_signedData: SignedData()}),
        ),
        (
            (
                "content",
                decode_path_defby(id_signedData),
                "encapContentInfo",
                "eContentType",
            ),
            ("eContent", {
                id_cct_PKIData: PKIData(),
                id_cct_PKIResponse: PKIResponse(),
            }),
        ),
        (
            (
                "content",
                decode_path_defby(id_signedData),
                "encapContentInfo",
                "eContent",
                decode_path_defby(id_cct_PKIResponse),
                "controlSequence",
                any,
                "attrType",
            ),
            ("attrValues", {
                id_cmc_recipientNonce: RecipientNonce(),
                id_cmc_senderNonce: SenderNonce(),
                id_cmc_statusInfoV2: CMCStatusInfoV2(),
                id_cmc_transactionId: TransactionId(),
            }),
        ),
    ))

Pay attention for :py:func:`pyderasn.decode_path_defby` and ``any``.
First function is useful for path construction when some automatic
decoding is already done. ``any`` is used for human readability and
means literally any value it meet -- useful for sequence and set of-s.

Primitive types
---------------

Boolean
_______
.. autoclass:: pyderasn.Boolean
   :members: __init__

Integer
_______
.. autoclass:: pyderasn.Integer
   :members: __init__

BitString
_________
.. autoclass:: pyderasn.BitString
   :members: __init__

OctetString
___________
.. autoclass:: pyderasn.OctetString
   :members: __init__

Null
____
.. autoclass:: pyderasn.Null
   :members: __init__

ObjectIdentifier
________________
.. autoclass:: pyderasn.ObjectIdentifier
   :members: __init__

Enumerated
__________
.. autoclass:: pyderasn.Enumerated

CommonString
____________
.. autoclass:: pyderasn.CommonString

UTCTime
_______
.. autoclass:: pyderasn.UTCTime
   :members: __init__, todatetime

GeneralizedTime
_______________
.. autoclass:: pyderasn.GeneralizedTime

Special types
-------------

Choice
______
.. autoclass:: pyderasn.Choice
   :members: __init__

PrimitiveTypes
______________
.. autoclass:: PrimitiveTypes

Any
___
.. autoclass:: pyderasn.Any
   :members: __init__

Constructed types
-----------------

Sequence
________
.. autoclass:: pyderasn.Sequence
   :members: __init__

Set
___
.. autoclass:: pyderasn.Set
   :members: __init__

SequenceOf
__________
.. autoclass:: pyderasn.SequenceOf
   :members: __init__

SetOf
_____
.. autoclass:: pyderasn.SetOf
   :members: __init__

Various
-------

.. autofunction:: pyderasn.hexenc
.. autofunction:: pyderasn.hexdec
.. autofunction:: pyderasn.tag_encode
.. autofunction:: pyderasn.tag_decode
.. autofunction:: pyderasn.tag_ctxp
.. autofunction:: pyderasn.tag_ctxc
.. autoclass:: pyderasn.Obj
"""

from codecs import getdecoder
from codecs import getencoder
from collections import namedtuple
from collections import OrderedDict
from datetime import datetime
from math import ceil

from six import add_metaclass
from six import binary_type
from six import byte2int
from six import indexbytes
from six import int2byte
from six import integer_types
from six import iterbytes
from six import PY2
from six import string_types
from six import text_type
from six.moves import xrange as six_xrange


__all__ = (
    "Any",
    "BitString",
    "BMPString",
    "Boolean",
    "BoundsError",
    "Choice",
    "decode_path_defby",
    "DecodeError",
    "Enumerated",
    "GeneralizedTime",
    "GeneralString",
    "GraphicString",
    "hexdec",
    "hexenc",
    "IA5String",
    "Integer",
    "InvalidLength",
    "InvalidOID",
    "InvalidValueType",
    "ISO646String",
    "NotEnoughData",
    "Null",
    "NumericString",
    "obj_by_path",
    "ObjectIdentifier",
    "ObjNotReady",
    "ObjUnknown",
    "OctetString",
    "PrimitiveTypes",
    "PrintableString",
    "Sequence",
    "SequenceOf",
    "Set",
    "SetOf",
    "T61String",
    "tag_ctxc",
    "tag_ctxp",
    "tag_decode",
    "TagClassApplication",
    "TagClassContext",
    "TagClassPrivate",
    "TagClassUniversal",
    "TagFormConstructed",
    "TagFormPrimitive",
    "TagMismatch",
    "TeletexString",
    "UniversalString",
    "UTCTime",
    "UTF8String",
    "VideotexString",
    "VisibleString",
)

TagClassUniversal = 0
TagClassApplication = 1 << 6
TagClassContext = 1 << 7
TagClassPrivate = 1 << 6 | 1 << 7
TagFormPrimitive = 0
TagFormConstructed = 1 << 5
TagClassReprs = {
    TagClassContext: "",
    TagClassApplication: "APPLICATION ",
    TagClassPrivate: "PRIVATE ",
    TagClassUniversal: "UNIV ",
}


########################################################################
# Errors
########################################################################

class DecodeError(Exception):
    def __init__(self, msg="", klass=None, decode_path=(), offset=0):
        """
        :param str msg: reason of decode failing
        :param klass: optional exact DecodeError inherited class (like
                      :py:exc:`NotEnoughData`, :py:exc:`TagMismatch`,
                      :py:exc:`InvalidLength`)
        :param decode_path: tuple of strings. It contains human
                            readable names of the fields through which
                            decoding process has passed
        :param int offset: binary offset where failure happened
        """
        super(DecodeError, self).__init__()
        self.msg = msg
        self.klass = klass
        self.decode_path = decode_path
        self.offset = offset

    def __str__(self):
        return " ".join(
            c for c in (
                "" if self.klass is None else self.klass.__name__,
                (
                    ("(%s)" % ".".join(self.decode_path))
                    if len(self.decode_path) > 0 else ""
                ),
                ("(at %d)" % self.offset) if self.offset > 0 else "",
                self.msg,
            ) if c != ""
        )

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self)


class NotEnoughData(DecodeError):
    pass


class TagMismatch(DecodeError):
    pass


class InvalidLength(DecodeError):
    pass


class InvalidOID(DecodeError):
    pass


class ObjUnknown(ValueError):
    def __init__(self, name):
        super(ObjUnknown, self).__init__()
        self.name = name

    def __str__(self):
        return "object is unknown: %s" % self.name

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self)


class ObjNotReady(ValueError):
    def __init__(self, name):
        super(ObjNotReady, self).__init__()
        self.name = name

    def __str__(self):
        return "object is not ready: %s" % self.name

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self)


class InvalidValueType(ValueError):
    def __init__(self, expected_types):
        super(InvalidValueType, self).__init__()
        self.expected_types = expected_types

    def __str__(self):
        return "invalid value type, expected: %s" % ", ".join(
            [repr(t) for t in self.expected_types]
        )

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self)


class BoundsError(ValueError):
    def __init__(self, bound_min, value, bound_max):
        super(BoundsError, self).__init__()
        self.bound_min = bound_min
        self.value = value
        self.bound_max = bound_max

    def __str__(self):
        return "unsatisfied bounds: %s <= %s <= %s" % (
            self.bound_min,
            self.value,
            self.bound_max,
        )

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self)


########################################################################
# Basic coders
########################################################################

_hexdecoder = getdecoder("hex")
_hexencoder = getencoder("hex")


def hexdec(data):
    """Binary data to hexadecimal string convert
    """
    return _hexdecoder(data)[0]


def hexenc(data):
    """Hexadecimal string to binary data convert
    """
    return _hexencoder(data)[0].decode("ascii")


def int_bytes_len(num, byte_len=8):
    if num == 0:
        return 1
    return int(ceil(float(num.bit_length()) / byte_len))


def zero_ended_encode(num):
    octets = bytearray(int_bytes_len(num, 7))
    i = len(octets) - 1
    octets[i] = num & 0x7F
    num >>= 7
    i -= 1
    while num > 0:
        octets[i] = 0x80 | (num & 0x7F)
        num >>= 7
        i -= 1
    return bytes(octets)


def tag_encode(num, klass=TagClassUniversal, form=TagFormPrimitive):
    """Encode tag to binary form

    :param int num: tag's number
    :param int klass: tag's class (:py:data:`pyderasn.TagClassUniversal`,
                      :py:data:`pyderasn.TagClassContext`,
                      :py:data:`pyderasn.TagClassApplication`,
                      :py:data:`pyderasn.TagClassPrivate`)
    :param int form: tag's form (:py:data:`pyderasn.TagFormPrimitive`,
                     :py:data:`pyderasn.TagFormConstructed`)
    """
    if num < 31:
        # [XX|X|.....]
        return int2byte(klass | form | num)
    # [XX|X|11111][1.......][1.......] ... [0.......]
    return int2byte(klass | form | 31) + zero_ended_encode(num)


def tag_decode(tag):
    """Decode tag from binary form

    .. warning::

       No validation is performed, assuming that it has already passed.

    It returns tuple with three integers, as
    :py:func:`pyderasn.tag_encode` accepts.
    """
    first_octet = byte2int(tag)
    klass = first_octet & 0xC0
    form = first_octet & 0x20
    if first_octet & 0x1F < 0x1F:
        return (klass, form, first_octet & 0x1F)
    num = 0
    for octet in iterbytes(tag[1:]):
        num <<= 7
        num |= octet & 0x7F
    return (klass, form, num)


def tag_ctxp(num):
    """Create CONTEXT PRIMITIVE tag
    """
    return tag_encode(num=num, klass=TagClassContext, form=TagFormPrimitive)


def tag_ctxc(num):
    """Create CONTEXT CONSTRUCTED tag
    """
    return tag_encode(num=num, klass=TagClassContext, form=TagFormConstructed)


def tag_strip(data):
    """Take off tag from the data

    :returns: (encoded tag, tag length, remaining data)
    """
    if len(data) == 0:
        raise NotEnoughData("no data at all")
    if byte2int(data) & 0x1F < 31:
        return data[:1], 1, data[1:]
    i = 0
    while True:
        i += 1
        if i == len(data):
            raise DecodeError("unfinished tag")
        if indexbytes(data, i) & 0x80 == 0:
            break
    i += 1
    return data[:i], i, data[i:]


def len_encode(l):
    if l < 0x80:
        return int2byte(l)
    octets = bytearray(int_bytes_len(l) + 1)
    octets[0] = 0x80 | (len(octets) - 1)
    for i in six_xrange(len(octets) - 1, 0, -1):
        octets[i] = l & 0xFF
        l >>= 8
    return bytes(octets)


def len_decode(data):
    if len(data) == 0:
        raise NotEnoughData("no data at all")
    first_octet = byte2int(data)
    if first_octet & 0x80 == 0:
        return first_octet, 1, data[1:]
    octets_num = first_octet & 0x7F
    if octets_num + 1 > len(data):
        raise NotEnoughData("encoded length is longer than data")
    if octets_num == 0:
        raise DecodeError("long form instead of short one")
    if byte2int(data[1:]) == 0:
        raise DecodeError("leading zeros")
    l = 0
    for v in iterbytes(data[1:1 + octets_num]):
        l = (l << 8) | v
    if l <= 127:
        raise DecodeError("long form instead of short one")
    return l, 1 + octets_num, data[1 + octets_num:]


########################################################################
# Base class
########################################################################

class AutoAddSlots(type):
    def __new__(cls, name, bases, _dict):
        _dict["__slots__"] = _dict.get("__slots__", ())
        return type.__new__(cls, name, bases, _dict)


@add_metaclass(AutoAddSlots)
class Obj(object):
    """Common ASN.1 object class

    All ASN.1 types are inherited from it. It has metaclass that
    automatically adds ``__slots__`` to all inherited classes.
    """
    __slots__ = (
        "tag",
        "_value",
        "_expl",
        "default",
        "optional",
        "offset",
        "llen",
        "vlen",
    )

    def __init__(
            self,
            impl=None,
            expl=None,
            default=None,
            optional=False,
            _decoded=(0, 0, 0),
    ):
        self.tag = getattr(self, "impl", self.tag_default) if impl is None else impl
        self._expl = getattr(self, "expl", None) if expl is None else expl
        if self.tag != self.tag_default and self._expl is not None:
            raise ValueError(
                "implicit and explicit tags can not be set simultaneously"
            )
        if default is not None:
            optional = True
        self.optional = optional
        self.offset, self.llen, self.vlen = _decoded
        self.default = None

    @property
    def ready(self):  # pragma: no cover
        """Is object ready to be encoded?
        """
        raise NotImplementedError()

    def _assert_ready(self):
        if not self.ready:
            raise ObjNotReady(self.__class__.__name__)

    @property
    def decoded(self):
        """Is object decoded?
        """
        return (self.llen + self.vlen) > 0

    def copy(self):  # pragma: no cover
        """Make a copy of object, safe to be mutated
        """
        raise NotImplementedError()

    @property
    def tlen(self):
        return len(self.tag)

    @property
    def tlvlen(self):
        return self.tlen + self.llen + self.vlen

    def __str__(self):  # pragma: no cover
        return self.__bytes__() if PY2 else self.__unicode__()

    def __ne__(self, their):
        return not(self == their)

    def __gt__(self, their):  # pragma: no cover
        return not(self < their)

    def __le__(self, their):  # pragma: no cover
        return (self == their) or (self < their)

    def __ge__(self, their):  # pragma: no cover
        return (self == their) or (self > their)

    def _encode(self):  # pragma: no cover
        raise NotImplementedError()

    def _decode(self, tlv, offset=0, decode_path=(), defines_by_path=None):  # pragma: no cover
        raise NotImplementedError()

    def encode(self):
        raw = self._encode()
        if self._expl is None:
            return raw
        return b"".join((self._expl, len_encode(len(raw)), raw))

    def decode(self, data, offset=0, leavemm=False, decode_path=(), defines_by_path=None):
        """Decode the data

        :param data: either binary or memoryview
        :param int offset: initial data's offset
        :param bool leavemm: do we need to leave memoryview of remaining
                    data as is, or convert it to bytes otherwise
        :param defines_by_path: :ref:`Read about DEFINED BY <definedby>`
        :returns: (Obj, remaining data)
        """
        tlv = memoryview(data)
        if self._expl is None:
            obj, tail = self._decode(
                tlv,
                offset,
                decode_path=decode_path,
                defines_by_path=defines_by_path,
            )
        else:
            try:
                t, tlen, lv = tag_strip(tlv)
            except DecodeError as err:
                raise err.__class__(
                    msg=err.msg,
                    klass=self.__class__,
                    decode_path=decode_path,
                    offset=offset,
                )
            if t != self._expl:
                raise TagMismatch(
                    klass=self.__class__,
                    decode_path=decode_path,
                    offset=offset,
                )
            try:
                l, llen, v = len_decode(lv)
            except DecodeError as err:
                raise err.__class__(
                    msg=err.msg,
                    klass=self.__class__,
                    decode_path=decode_path,
                    offset=offset,
                )
            if l > len(v):
                raise NotEnoughData(
                    "encoded length is longer than data",
                    klass=self.__class__,
                    decode_path=decode_path,
                    offset=offset,
                )
            obj, tail = self._decode(
                v,
                offset=offset + tlen + llen,
                decode_path=decode_path,
                defines_by_path=defines_by_path,
            )
        return obj, (tail if leavemm else tail.tobytes())

    @property
    def expled(self):
        return self._expl is not None

    @property
    def expl_tag(self):
        return self._expl

    @property
    def expl_tlen(self):
        return len(self._expl)

    @property
    def expl_llen(self):
        return len(len_encode(self.tlvlen))

    @property
    def expl_offset(self):
        return self.offset - self.expl_tlen - self.expl_llen

    @property
    def expl_vlen(self):
        return self.tlvlen

    @property
    def expl_tlvlen(self):
        return self.expl_tlen + self.expl_llen + self.expl_vlen


def decode_path_defby(defined_by):
    """DEFINED BY representation inside decode path
    """
    return "DEFINED BY (%s)" % defined_by


########################################################################
# Pretty printing
########################################################################

PP = namedtuple("PP", (
    "asn1_type_name",
    "obj_name",
    "decode_path",
    "value",
    "blob",
    "optional",
    "default",
    "impl",
    "expl",
    "offset",
    "tlen",
    "llen",
    "vlen",
    "expl_offset",
    "expl_tlen",
    "expl_llen",
    "expl_vlen",
))


def _pp(
        asn1_type_name="unknown",
        obj_name="unknown",
        decode_path=(),
        value=None,
        blob=None,
        optional=False,
        default=False,
        impl=None,
        expl=None,
        offset=0,
        tlen=0,
        llen=0,
        vlen=0,
        expl_offset=None,
        expl_tlen=None,
        expl_llen=None,
        expl_vlen=None,
):
    return PP(
        asn1_type_name,
        obj_name,
        decode_path,
        value,
        blob,
        optional,
        default,
        impl,
        expl,
        offset,
        tlen,
        llen,
        vlen,
        expl_offset,
        expl_tlen,
        expl_llen,
        expl_vlen,
    )


def pp_console_row(pp, oids=None, with_offsets=False, with_blob=True):
    cols = []
    if with_offsets:
        cols.append("%5d%s [%d,%d,%4d]" % (
            pp.offset,
            (
                "  " if pp.expl_offset is None else
                ("-%d" % (pp.offset - pp.expl_offset))
            ),
            pp.tlen,
            pp.llen,
            pp.vlen,
        ))
    if len(pp.decode_path) > 0:
        cols.append(" ." * (len(pp.decode_path)))
        cols.append("%s:" % pp.decode_path[-1])
    if pp.expl is not None:
        klass, _, num = pp.expl
        cols.append("[%s%d] EXPLICIT" % (TagClassReprs[klass], num))
    if pp.impl is not None:
        klass, _, num = pp.impl
        cols.append("[%s%d]" % (TagClassReprs[klass], num))
    if pp.asn1_type_name.replace(" ", "") != pp.obj_name.upper():
        cols.append(pp.obj_name)
    cols.append(pp.asn1_type_name)
    if pp.value is not None:
        value = pp.value
        if (
                oids is not None and
                pp.asn1_type_name == ObjectIdentifier.asn1_type_name and
                value in oids
        ):
            value = "%s (%s)" % (oids[value], pp.value)
        cols.append(value)
    if with_blob:
        if isinstance(pp.blob, binary_type):
            cols.append(hexenc(pp.blob))
        elif isinstance(pp.blob, tuple):
            cols.append(", ".join(pp.blob))
    if pp.optional:
        cols.append("OPTIONAL")
    if pp.default:
        cols.append("DEFAULT")
    return " ".join(cols)


def pp_console_blob(pp):
    cols = [" " * len("XXXXXYY [X,X,XXXX]")]
    if len(pp.decode_path) > 0:
        cols.append(" ." * (len(pp.decode_path) + 1))
    if isinstance(pp.blob, binary_type):
        blob = hexenc(pp.blob).upper()
        for i in range(0, len(blob), 32):
            chunk = blob[i:i + 32]
            yield " ".join(cols + [":".join(
                chunk[j:j + 2] for j in range(0, len(chunk), 2)
            )])
    elif isinstance(pp.blob, tuple):
        yield " ".join(cols + [", ".join(pp.blob)])


def pprint(obj, oids=None, big_blobs=False):
    """Pretty print object

    :param Obj obj: object you want to pretty print
    :param oids: ``OID <-> humand readable string`` dictionary. When OID
                 from it is met, then its humand readable form is printed
    :param big_blobs: if large binary objects are met (like OctetString
                      values), do we need to print them too, on separate
                      lines
    """
    def _pprint_pps(pps):
        for pp in pps:
            if hasattr(pp, "_fields"):
                if big_blobs:
                    yield pp_console_row(
                        pp,
                        oids=oids,
                        with_offsets=True,
                        with_blob=False,
                    )
                    for row in pp_console_blob(pp):
                        yield row
                else:
                    yield pp_console_row(pp, oids=oids, with_offsets=True)
            else:
                for row in _pprint_pps(pp):
                    yield row
    return "\n".join(_pprint_pps(obj.pps()))


########################################################################
# ASN.1 primitive types
########################################################################

class Boolean(Obj):
    """``BOOLEAN`` boolean type

    >>> b = Boolean(True)
    BOOLEAN True
    >>> b == Boolean(True)
    True
    >>> bool(b)
    True
    """
    __slots__ = ()
    tag_default = tag_encode(1)
    asn1_type_name = "BOOLEAN"

    def __init__(
            self,
            value=None,
            impl=None,
            expl=None,
            default=None,
            optional=False,
            _decoded=(0, 0, 0),
    ):
        """
        :param value: set the value. Either boolean type, or
                      :py:class:`pyderasn.Boolean` object
        :param bytes impl: override default tag with ``IMPLICIT`` one
        :param bytes expl: override default tag with ``EXPLICIT`` one
        :param default: set default value. Type same as in ``value``
        :param bool optional: is object ``OPTIONAL`` in sequence
        """
        super(Boolean, self).__init__(impl, expl, default, optional, _decoded)
        self._value = None if value is None else self._value_sanitize(value)
        if default is not None:
            default = self._value_sanitize(default)
            self.default = self.__class__(
                value=default,
                impl=self.tag,
                expl=self._expl,
            )
            if value is None:
                self._value = default

    def _value_sanitize(self, value):
        if issubclass(value.__class__, Boolean):
            return value._value
        if isinstance(value, bool):
            return value
        raise InvalidValueType((self.__class__, bool))

    @property
    def ready(self):
        return self._value is not None

    def copy(self):
        obj = self.__class__()
        obj._value = self._value
        obj.tag = self.tag
        obj._expl = self._expl
        obj.default = self.default
        obj.optional = self.optional
        obj.offset = self.offset
        obj.llen = self.llen
        obj.vlen = self.vlen
        return obj

    def __nonzero__(self):
        self._assert_ready()
        return self._value

    def __bool__(self):
        self._assert_ready()
        return self._value

    def __eq__(self, their):
        if isinstance(their, bool):
            return self._value == their
        if not issubclass(their.__class__, Boolean):
            return False
        return (
            self._value == their._value and
            self.tag == their.tag and
            self._expl == their._expl
        )

    def __call__(
            self,
            value=None,
            impl=None,
            expl=None,
            default=None,
            optional=None,
    ):
        return self.__class__(
            value=value,
            impl=self.tag if impl is None else impl,
            expl=self._expl if expl is None else expl,
            default=self.default if default is None else default,
            optional=self.optional if optional is None else optional,
        )

    def _encode(self):
        self._assert_ready()
        return b"".join((
            self.tag,
            len_encode(1),
            (b"\xFF" if self._value else b"\x00"),
        ))

    def _decode(self, tlv, offset=0, decode_path=(), defines_by_path=None):
        try:
            t, _, lv = tag_strip(tlv)
        except DecodeError as err:
            raise err.__class__(
                msg=err.msg,
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        if t != self.tag:
            raise TagMismatch(
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        try:
            l, _, v = len_decode(lv)
        except DecodeError as err:
            raise err.__class__(
                msg=err.msg,
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        if l != 1:
            raise InvalidLength(
                "Boolean's length must be equal to 1",
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        if l > len(v):
            raise NotEnoughData(
                "encoded length is longer than data",
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        first_octet = byte2int(v)
        if first_octet == 0:
            value = False
        elif first_octet == 0xFF:
            value = True
        else:
            raise DecodeError(
                "unacceptable Boolean value",
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        obj = self.__class__(
            value=value,
            impl=self.tag,
            expl=self._expl,
            default=self.default,
            optional=self.optional,
            _decoded=(offset, 1, 1),
        )
        return obj, v[1:]

    def __repr__(self):
        return pp_console_row(next(self.pps()))

    def pps(self, decode_path=()):
        yield _pp(
            asn1_type_name=self.asn1_type_name,
            obj_name=self.__class__.__name__,
            decode_path=decode_path,
            value=str(self._value) if self.ready else None,
            optional=self.optional,
            default=self == self.default,
            impl=None if self.tag == self.tag_default else tag_decode(self.tag),
            expl=None if self._expl is None else tag_decode(self._expl),
            offset=self.offset,
            tlen=self.tlen,
            llen=self.llen,
            vlen=self.vlen,
            expl_offset=self.expl_offset if self.expled else None,
            expl_tlen=self.expl_tlen if self.expled else None,
            expl_llen=self.expl_llen if self.expled else None,
            expl_vlen=self.expl_vlen if self.expled else None,
        )


class Integer(Obj):
    """``INTEGER`` integer type

    >>> b = Integer(-123)
    INTEGER -123
    >>> b == Integer(-123)
    True
    >>> int(b)
    -123

    >>> Integer(2, bounds=(1, 3))
    INTEGER 2
    >>> Integer(5, bounds=(1, 3))
    Traceback (most recent call last):
    pyderasn.BoundsError: unsatisfied bounds: 1 <= 5 <= 3

    ::

        class Version(Integer):
            schema = (
                ("v1", 0),
                ("v2", 1),
                ("v3", 2),
            )

    >>> v = Version("v1")
    Version INTEGER v1
    >>> int(v)
    0
    >>> v.named
    'v1'
    >>> v.specs
    {'v3': 2, 'v1': 0, 'v2': 1}
    """
    __slots__ = ("specs", "_bound_min", "_bound_max")
    tag_default = tag_encode(2)
    asn1_type_name = "INTEGER"

    def __init__(
            self,
            value=None,
            bounds=None,
            impl=None,
            expl=None,
            default=None,
            optional=False,
            _specs=None,
            _decoded=(0, 0, 0),
    ):
        """
        :param value: set the value. Either integer type, named value
                      (if ``schema`` is specified in the class), or
                      :py:class:`pyderasn.Integer` object
        :param bounds: set ``(MIN, MAX)`` value constraint.
                       (-inf, +inf) by default
        :param bytes impl: override default tag with ``IMPLICIT`` one
        :param bytes expl: override default tag with ``EXPLICIT`` one
        :param default: set default value. Type same as in ``value``
        :param bool optional: is object ``OPTIONAL`` in sequence
        """
        super(Integer, self).__init__(impl, expl, default, optional, _decoded)
        self._value = value
        specs = getattr(self, "schema", {}) if _specs is None else _specs
        self.specs = specs if isinstance(specs, dict) else dict(specs)
        self._bound_min, self._bound_max = getattr(
            self,
            "bounds",
            (float("-inf"), float("+inf")),
        ) if bounds is None else bounds
        if value is not None:
            self._value = self._value_sanitize(value)
        if default is not None:
            default = self._value_sanitize(default)
            self.default = self.__class__(
                value=default,
                impl=self.tag,
                expl=self._expl,
                _specs=self.specs,
            )
            if self._value is None:
                self._value = default

    def _value_sanitize(self, value):
        if issubclass(value.__class__, Integer):
            value = value._value
        elif isinstance(value, integer_types):
            pass
        elif isinstance(value, str):
            value = self.specs.get(value)
            if value is None:
                raise ObjUnknown("integer value: %s" % value)
        else:
            raise InvalidValueType((self.__class__, int, str))
        if not self._bound_min <= value <= self._bound_max:
            raise BoundsError(self._bound_min, value, self._bound_max)
        return value

    @property
    def ready(self):
        return self._value is not None

    def copy(self):
        obj = self.__class__(_specs=self.specs)
        obj._value = self._value
        obj._bound_min = self._bound_min
        obj._bound_max = self._bound_max
        obj.tag = self.tag
        obj._expl = self._expl
        obj.default = self.default
        obj.optional = self.optional
        obj.offset = self.offset
        obj.llen = self.llen
        obj.vlen = self.vlen
        return obj

    def __int__(self):
        self._assert_ready()
        return int(self._value)

    def __hash__(self):
        self._assert_ready()
        return hash(
            self.tag +
            bytes(self._expl or b"") +
            str(self._value).encode("ascii"),
        )

    def __eq__(self, their):
        if isinstance(their, integer_types):
            return self._value == their
        if not issubclass(their.__class__, Integer):
            return False
        return (
            self._value == their._value and
            self.tag == their.tag and
            self._expl == their._expl
        )

    def __lt__(self, their):
        return self._value < their._value

    @property
    def named(self):
        for name, value in self.specs.items():
            if value == self._value:
                return name

    def __call__(
            self,
            value=None,
            bounds=None,
            impl=None,
            expl=None,
            default=None,
            optional=None,
    ):
        return self.__class__(
            value=value,
            bounds=(
                (self._bound_min, self._bound_max)
                if bounds is None else bounds
            ),
            impl=self.tag if impl is None else impl,
            expl=self._expl if expl is None else expl,
            default=self.default if default is None else default,
            optional=self.optional if optional is None else optional,
            _specs=self.specs,
        )

    def _encode(self):
        self._assert_ready()
        value = self._value
        if PY2:
            if value == 0:
                octets = bytearray([0])
            elif value < 0:
                value = -value
                value -= 1
                octets = bytearray()
                while value > 0:
                    octets.append((value & 0xFF) ^ 0xFF)
                    value >>= 8
                if len(octets) == 0 or octets[-1] & 0x80 == 0:
                    octets.append(0xFF)
            else:
                octets = bytearray()
                while value > 0:
                    octets.append(value & 0xFF)
                    value >>= 8
                if octets[-1] & 0x80 > 0:
                    octets.append(0x00)
            octets.reverse()
            octets = bytes(octets)
        else:
            bytes_len = ceil(value.bit_length() / 8) or 1
            while True:
                try:
                    octets = value.to_bytes(
                        bytes_len,
                        byteorder="big",
                        signed=True,
                    )
                except OverflowError:
                    bytes_len += 1
                else:
                    break
        return b"".join((self.tag, len_encode(len(octets)), octets))

    def _decode(self, tlv, offset=0, decode_path=(), defines_by_path=None):
        try:
            t, _, lv = tag_strip(tlv)
        except DecodeError as err:
            raise err.__class__(
                msg=err.msg,
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        if t != self.tag:
            raise TagMismatch(
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        try:
            l, llen, v = len_decode(lv)
        except DecodeError as err:
            raise err.__class__(
                msg=err.msg,
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        if l > len(v):
            raise NotEnoughData(
                "encoded length is longer than data",
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        if l == 0:
            raise NotEnoughData(
                "zero length",
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        v, tail = v[:l], v[l:]
        first_octet = byte2int(v)
        if l > 1:
            second_octet = byte2int(v[1:])
            if (
                    ((first_octet == 0x00) and (second_octet & 0x80 == 0)) or
                    ((first_octet == 0xFF) and (second_octet & 0x80 != 0))
            ):
                raise DecodeError(
                    "non normalized integer",
                    klass=self.__class__,
                    decode_path=decode_path,
                    offset=offset,
                )
        if PY2:
            value = 0
            if first_octet & 0x80 > 0:
                octets = bytearray()
                for octet in bytearray(v):
                    octets.append(octet ^ 0xFF)
                for octet in octets:
                    value = (value << 8) | octet
                value += 1
                value = -value
            else:
                for octet in bytearray(v):
                    value = (value << 8) | octet
        else:
            value = int.from_bytes(v, byteorder="big", signed=True)
        try:
            obj = self.__class__(
                value=value,
                bounds=(self._bound_min, self._bound_max),
                impl=self.tag,
                expl=self._expl,
                default=self.default,
                optional=self.optional,
                _specs=self.specs,
                _decoded=(offset, llen, l),
            )
        except BoundsError as err:
            raise DecodeError(
                msg=str(err),
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        return obj, tail

    def __repr__(self):
        return pp_console_row(next(self.pps()))

    def pps(self, decode_path=()):
        yield _pp(
            asn1_type_name=self.asn1_type_name,
            obj_name=self.__class__.__name__,
            decode_path=decode_path,
            value=(self.named or str(self._value)) if self.ready else None,
            optional=self.optional,
            default=self == self.default,
            impl=None if self.tag == self.tag_default else tag_decode(self.tag),
            expl=None if self._expl is None else tag_decode(self._expl),
            offset=self.offset,
            tlen=self.tlen,
            llen=self.llen,
            vlen=self.vlen,
            expl_offset=self.expl_offset if self.expled else None,
            expl_tlen=self.expl_tlen if self.expled else None,
            expl_llen=self.expl_llen if self.expled else None,
            expl_vlen=self.expl_vlen if self.expled else None,
        )


class BitString(Obj):
    """``BIT STRING`` bit string type

    >>> BitString(b"hello world")
    BIT STRING 88 bits 68656c6c6f20776f726c64
    >>> bytes(b)
    b'hello world'
    >>> b == b"hello world"
    True
    >>> b.bit_len
    88

    >>> b = BitString("'010110000000'B")
    BIT STRING 12 bits 5800
    >>> b.bit_len
    12
    >>> b[0], b[1], b[2], b[3]
    (False, True, False, True)
    >>> b[1000]
    False
    >>> [v for v in b]
    [False, True, False, True, True, False, False, False, False, False, False, False]

    ::

        class KeyUsage(BitString):
            schema = (
                ('digitalSignature', 0),
                ('nonRepudiation', 1),
                ('keyEncipherment', 2),
            )

    >>> b = KeyUsage(('keyEncipherment', 'nonRepudiation'))
    KeyUsage BIT STRING 3 bits nonRepudiation, keyEncipherment
    >>> b.named
    ['nonRepudiation', 'keyEncipherment']
    >>> b.specs
    {'nonRepudiation': 1, 'digitalSignature': 0, 'keyEncipherment': 2}
    """
    __slots__ = ("specs",)
    tag_default = tag_encode(3)
    asn1_type_name = "BIT STRING"

    def __init__(
            self,
            value=None,
            impl=None,
            expl=None,
            default=None,
            optional=False,
            _specs=None,
            _decoded=(0, 0, 0),
    ):
        """
        :param value: set the value. Either binary type, tuple of named
                      values (if ``schema`` is specified in the class),
                      string in ``'XXX...'B`` form, or
                      :py:class:`pyderasn.BitString` object
        :param bytes impl: override default tag with ``IMPLICIT`` one
        :param bytes expl: override default tag with ``EXPLICIT`` one
        :param default: set default value. Type same as in ``value``
        :param bool optional: is object ``OPTIONAL`` in sequence
        """
        super(BitString, self).__init__(impl, expl, default, optional, _decoded)
        specs = getattr(self, "schema", {}) if _specs is None else _specs
        self.specs = specs if isinstance(specs, dict) else dict(specs)
        self._value = None if value is None else self._value_sanitize(value)
        if default is not None:
            default = self._value_sanitize(default)
            self.default = self.__class__(
                value=default,
                impl=self.tag,
                expl=self._expl,
            )
            if value is None:
                self._value = default

    def _bits2octets(self, bits):
        if len(self.specs) > 0:
            bits = bits.rstrip("0")
        bit_len = len(bits)
        bits += "0" * ((8 - (bit_len % 8)) % 8)
        octets = bytearray(len(bits) // 8)
        for i in six_xrange(len(octets)):
            octets[i] = int(bits[i * 8:(i * 8) + 8], 2)
        return bit_len, bytes(octets)

    def _value_sanitize(self, value):
        if issubclass(value.__class__, BitString):
            return value._value
        if isinstance(value, (string_types, binary_type)):
            if (
                    isinstance(value, string_types) and
                    value.startswith("'") and
                    value.endswith("'B")
            ):
                value = value[1:-2]
                if not set(value) <= set(("0", "1")):
                    raise ValueError("B's coding contains unacceptable chars")
                return self._bits2octets(value)
            elif isinstance(value, binary_type):
                return (len(value) * 8, value)
            else:
                raise InvalidValueType((
                    self.__class__,
                    string_types,
                    binary_type,
                ))
        if isinstance(value, tuple):
            if (
                    len(value) == 2 and
                    isinstance(value[0], integer_types) and
                    isinstance(value[1], binary_type)
            ):
                return value
            bits = []
            for name in value:
                bit = self.specs.get(name)
                if bit is None:
                    raise ObjUnknown("BitString value: %s" % name)
                bits.append(bit)
            if len(bits) == 0:
                return self._bits2octets("")
            bits = set(bits)
            return self._bits2octets("".join(
                ("1" if bit in bits else "0")
                for bit in six_xrange(max(bits) + 1)
            ))
        raise InvalidValueType((self.__class__, binary_type, string_types))

    @property
    def ready(self):
        return self._value is not None

    def copy(self):
        obj = self.__class__(_specs=self.specs)
        value = self._value
        if value is not None:
            value = (value[0], value[1])
        obj._value = value
        obj.tag = self.tag
        obj._expl = self._expl
        obj.default = self.default
        obj.optional = self.optional
        obj.offset = self.offset
        obj.llen = self.llen
        obj.vlen = self.vlen
        return obj

    def __iter__(self):
        self._assert_ready()
        for i in six_xrange(self._value[0]):
            yield self[i]

    @property
    def bit_len(self):
        self._assert_ready()
        return self._value[0]

    def __bytes__(self):
        self._assert_ready()
        return self._value[1]

    def __eq__(self, their):
        if isinstance(their, bytes):
            return self._value[1] == their
        if not issubclass(their.__class__, BitString):
            return False
        return (
            self._value == their._value and
            self.tag == their.tag and
            self._expl == their._expl
        )

    @property
    def named(self):
        return [name for name, bit in self.specs.items() if self[bit]]

    def __call__(
            self,
            value=None,
            impl=None,
            expl=None,
            default=None,
            optional=None,
    ):
        return self.__class__(
            value=value,
            impl=self.tag if impl is None else impl,
            expl=self._expl if expl is None else expl,
            default=self.default if default is None else default,
            optional=self.optional if optional is None else optional,
            _specs=self.specs,
        )

    def __getitem__(self, key):
        if isinstance(key, int):
            bit_len, octets = self._value
            if key >= bit_len:
                return False
            return (
                byte2int(memoryview(octets)[key // 8:]) >>
                (7 - (key % 8))
            ) & 1 == 1
        if isinstance(key, string_types):
            value = self.specs.get(key)
            if value is None:
                raise ObjUnknown("BitString value: %s" % key)
            return self[value]
        raise InvalidValueType((int, str))

    def _encode(self):
        self._assert_ready()
        bit_len, octets = self._value
        return b"".join((
            self.tag,
            len_encode(len(octets) + 1),
            int2byte((8 - bit_len % 8) % 8),
            octets,
        ))

    def _decode(self, tlv, offset=0, decode_path=(), defines_by_path=None):
        try:
            t, _, lv = tag_strip(tlv)
        except DecodeError as err:
            raise err.__class__(
                msg=err.msg,
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        if t != self.tag:
            raise TagMismatch(
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        try:
            l, llen, v = len_decode(lv)
        except DecodeError as err:
            raise err.__class__(
                msg=err.msg,
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        if l > len(v):
            raise NotEnoughData(
                "encoded length is longer than data",
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        if l == 0:
            raise NotEnoughData(
                "zero length",
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        pad_size = byte2int(v)
        if l == 1 and pad_size != 0:
            raise DecodeError(
                "invalid empty value",
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        if pad_size > 7:
            raise DecodeError(
                "too big pad",
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        if byte2int(v[-1:]) & ((1 << pad_size) - 1) != 0:
            raise DecodeError(
                "invalid pad",
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        v, tail = v[:l], v[l:]
        obj = self.__class__(
            value=((len(v) - 1) * 8 - pad_size, v[1:].tobytes()),
            impl=self.tag,
            expl=self._expl,
            default=self.default,
            optional=self.optional,
            _specs=self.specs,
            _decoded=(offset, llen, l),
        )
        return obj, tail

    def __repr__(self):
        return pp_console_row(next(self.pps()))

    def pps(self, decode_path=()):
        value = None
        blob = None
        if self.ready:
            bit_len, blob = self._value
            value = "%d bits" % bit_len
            if len(self.specs) > 0:
                blob = tuple(self.named)
        yield _pp(
            asn1_type_name=self.asn1_type_name,
            obj_name=self.__class__.__name__,
            decode_path=decode_path,
            value=value,
            blob=blob,
            optional=self.optional,
            default=self == self.default,
            impl=None if self.tag == self.tag_default else tag_decode(self.tag),
            expl=None if self._expl is None else tag_decode(self._expl),
            offset=self.offset,
            tlen=self.tlen,
            llen=self.llen,
            vlen=self.vlen,
            expl_offset=self.expl_offset if self.expled else None,
            expl_tlen=self.expl_tlen if self.expled else None,
            expl_llen=self.expl_llen if self.expled else None,
            expl_vlen=self.expl_vlen if self.expled else None,
        )


class OctetString(Obj):
    """``OCTET STRING`` binary string type

    >>> s = OctetString(b"hello world")
    OCTET STRING 11 bytes 68656c6c6f20776f726c64
    >>> s == OctetString(b"hello world")
    True
    >>> bytes(s)
    b'hello world'

    >>> OctetString(b"hello", bounds=(4, 4))
    Traceback (most recent call last):
    pyderasn.BoundsError: unsatisfied bounds: 4 <= 5 <= 4
    >>> OctetString(b"hell", bounds=(4, 4))
    OCTET STRING 4 bytes 68656c6c
    """
    __slots__ = ("_bound_min", "_bound_max", "defined")
    tag_default = tag_encode(4)
    asn1_type_name = "OCTET STRING"

    def __init__(
            self,
            value=None,
            bounds=None,
            impl=None,
            expl=None,
            default=None,
            optional=False,
            _decoded=(0, 0, 0),
    ):
        """
        :param value: set the value. Either binary type, or
                      :py:class:`pyderasn.OctetString` object
        :param bounds: set ``(MIN, MAX)`` value size constraint.
                       (-inf, +inf) by default
        :param bytes impl: override default tag with ``IMPLICIT`` one
        :param bytes expl: override default tag with ``EXPLICIT`` one
        :param default: set default value. Type same as in ``value``
        :param bool optional: is object ``OPTIONAL`` in sequence
        """
        super(OctetString, self).__init__(
            impl,
            expl,
            default,
            optional,
            _decoded,
        )
        self._value = value
        self._bound_min, self._bound_max = getattr(
            self,
            "bounds",
            (0, float("+inf")),
        ) if bounds is None else bounds
        if value is not None:
            self._value = self._value_sanitize(value)
        if default is not None:
            default = self._value_sanitize(default)
            self.default = self.__class__(
                value=default,
                impl=self.tag,
                expl=self._expl,
            )
            if self._value is None:
                self._value = default
        self.defined = None

    def _value_sanitize(self, value):
        if issubclass(value.__class__, OctetString):
            value = value._value
        elif isinstance(value, binary_type):
            pass
        else:
            raise InvalidValueType((self.__class__, bytes))
        if not self._bound_min <= len(value) <= self._bound_max:
            raise BoundsError(self._bound_min, len(value), self._bound_max)
        return value

    @property
    def ready(self):
        return self._value is not None

    def copy(self):
        obj = self.__class__()
        obj._value = self._value
        obj._bound_min = self._bound_min
        obj._bound_max = self._bound_max
        obj.tag = self.tag
        obj._expl = self._expl
        obj.default = self.default
        obj.optional = self.optional
        obj.offset = self.offset
        obj.llen = self.llen
        obj.vlen = self.vlen
        return obj

    def __bytes__(self):
        self._assert_ready()
        return self._value

    def __eq__(self, their):
        if isinstance(their, binary_type):
            return self._value == their
        if not issubclass(their.__class__, OctetString):
            return False
        return (
            self._value == their._value and
            self.tag == their.tag and
            self._expl == their._expl
        )

    def __lt__(self, their):
        return self._value < their._value

    def __call__(
            self,
            value=None,
            bounds=None,
            impl=None,
            expl=None,
            default=None,
            optional=None,
    ):
        return self.__class__(
            value=value,
            bounds=(
                (self._bound_min, self._bound_max)
                if bounds is None else bounds
            ),
            impl=self.tag if impl is None else impl,
            expl=self._expl if expl is None else expl,
            default=self.default if default is None else default,
            optional=self.optional if optional is None else optional,
        )

    def _encode(self):
        self._assert_ready()
        return b"".join((
            self.tag,
            len_encode(len(self._value)),
            self._value,
        ))

    def _decode(self, tlv, offset=0, decode_path=(), defines_by_path=None):
        try:
            t, _, lv = tag_strip(tlv)
        except DecodeError as err:
            raise err.__class__(
                msg=err.msg,
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        if t != self.tag:
            raise TagMismatch(
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        try:
            l, llen, v = len_decode(lv)
        except DecodeError as err:
            raise err.__class__(
                msg=err.msg,
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        if l > len(v):
            raise NotEnoughData(
                "encoded length is longer than data",
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        v, tail = v[:l], v[l:]
        try:
            obj = self.__class__(
                value=v.tobytes(),
                bounds=(self._bound_min, self._bound_max),
                impl=self.tag,
                expl=self._expl,
                default=self.default,
                optional=self.optional,
                _decoded=(offset, llen, l),
            )
        except BoundsError as err:
            raise DecodeError(
                msg=str(err),
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        return obj, tail

    def __repr__(self):
        return pp_console_row(next(self.pps()))

    def pps(self, decode_path=()):
        yield _pp(
            asn1_type_name=self.asn1_type_name,
            obj_name=self.__class__.__name__,
            decode_path=decode_path,
            value=("%d bytes" % len(self._value)) if self.ready else None,
            blob=self._value if self.ready else None,
            optional=self.optional,
            default=self == self.default,
            impl=None if self.tag == self.tag_default else tag_decode(self.tag),
            expl=None if self._expl is None else tag_decode(self._expl),
            offset=self.offset,
            tlen=self.tlen,
            llen=self.llen,
            vlen=self.vlen,
            expl_offset=self.expl_offset if self.expled else None,
            expl_tlen=self.expl_tlen if self.expled else None,
            expl_llen=self.expl_llen if self.expled else None,
            expl_vlen=self.expl_vlen if self.expled else None,
        )
        defined_by, defined = self.defined or (None, None)
        if defined_by is not None:
            yield defined.pps(
                decode_path=decode_path + (decode_path_defby(defined_by),)
            )


class Null(Obj):
    """``NULL`` null object

    >>> n = Null()
    NULL
    >>> n.ready
    True
    """
    __slots__ = ()
    tag_default = tag_encode(5)
    asn1_type_name = "NULL"

    def __init__(
            self,
            value=None,  # unused, but Sequence passes it
            impl=None,
            expl=None,
            optional=False,
            _decoded=(0, 0, 0),
    ):
        """
        :param bytes impl: override default tag with ``IMPLICIT`` one
        :param bytes expl: override default tag with ``EXPLICIT`` one
        :param bool optional: is object ``OPTIONAL`` in sequence
        """
        super(Null, self).__init__(impl, expl, None, optional, _decoded)
        self.default = None

    @property
    def ready(self):
        return True

    def copy(self):
        obj = self.__class__()
        obj.tag = self.tag
        obj._expl = self._expl
        obj.default = self.default
        obj.optional = self.optional
        obj.offset = self.offset
        obj.llen = self.llen
        obj.vlen = self.vlen
        return obj

    def __eq__(self, their):
        if not issubclass(their.__class__, Null):
            return False
        return (
            self.tag == their.tag and
            self._expl == their._expl
        )

    def __call__(
            self,
            value=None,
            impl=None,
            expl=None,
            optional=None,
    ):
        return self.__class__(
            impl=self.tag if impl is None else impl,
            expl=self._expl if expl is None else expl,
            optional=self.optional if optional is None else optional,
        )

    def _encode(self):
        return self.tag + len_encode(0)

    def _decode(self, tlv, offset=0, decode_path=(), defines_by_path=None):
        try:
            t, _, lv = tag_strip(tlv)
        except DecodeError as err:
            raise err.__class__(
                msg=err.msg,
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        if t != self.tag:
            raise TagMismatch(
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        try:
            l, _, v = len_decode(lv)
        except DecodeError as err:
            raise err.__class__(
                msg=err.msg,
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        if l != 0:
            raise InvalidLength(
                "Null must have zero length",
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        obj = self.__class__(
            impl=self.tag,
            expl=self._expl,
            optional=self.optional,
            _decoded=(offset, 1, 0),
        )
        return obj, v

    def __repr__(self):
        return pp_console_row(next(self.pps()))

    def pps(self, decode_path=()):
        yield _pp(
            asn1_type_name=self.asn1_type_name,
            obj_name=self.__class__.__name__,
            decode_path=decode_path,
            optional=self.optional,
            impl=None if self.tag == self.tag_default else tag_decode(self.tag),
            expl=None if self._expl is None else tag_decode(self._expl),
            offset=self.offset,
            tlen=self.tlen,
            llen=self.llen,
            vlen=self.vlen,
            expl_offset=self.expl_offset if self.expled else None,
            expl_tlen=self.expl_tlen if self.expled else None,
            expl_llen=self.expl_llen if self.expled else None,
            expl_vlen=self.expl_vlen if self.expled else None,
        )


class ObjectIdentifier(Obj):
    """``OBJECT IDENTIFIER`` OID type

    >>> oid = ObjectIdentifier((1, 2, 3))
    OBJECT IDENTIFIER 1.2.3
    >>> oid == ObjectIdentifier("1.2.3")
    True
    >>> tuple(oid)
    (1, 2, 3)
    >>> str(oid)
    '1.2.3'
    >>> oid + (4, 5) + ObjectIdentifier("1.7")
    OBJECT IDENTIFIER 1.2.3.4.5.1.7

    >>> str(ObjectIdentifier((3, 1)))
    Traceback (most recent call last):
    pyderasn.InvalidOID: unacceptable first arc value
    """
    __slots__ = ("defines",)
    tag_default = tag_encode(6)
    asn1_type_name = "OBJECT IDENTIFIER"

    def __init__(
            self,
            value=None,
            defines=None,
            impl=None,
            expl=None,
            default=None,
            optional=False,
            _decoded=(0, 0, 0),
    ):
        """
        :param value: set the value. Either tuples of integers,
                      string of "."-concatenated integers, or
                      :py:class:`pyderasn.ObjectIdentifier` object
        :param defines: tuple of two elements. First one is a name of
                        field inside :py:class:`pyderasn.Sequence`,
                        defining with that OID. Second element is a
                        ``{OID: pyderasn.Obj()}`` dictionary, mapping
                        between current OID value and structure applied
                        to defined field.
                        :ref:`Read about DEFINED BY <definedby>`
        :param bytes impl: override default tag with ``IMPLICIT`` one
        :param bytes expl: override default tag with ``EXPLICIT`` one
        :param default: set default value. Type same as in ``value``
        :param bool optional: is object ``OPTIONAL`` in sequence
        """
        super(ObjectIdentifier, self).__init__(
            impl,
            expl,
            default,
            optional,
            _decoded,
        )
        self._value = value
        if value is not None:
            self._value = self._value_sanitize(value)
        if default is not None:
            default = self._value_sanitize(default)
            self.default = self.__class__(
                value=default,
                impl=self.tag,
                expl=self._expl,
            )
            if self._value is None:
                self._value = default
        self.defines = defines

    def __add__(self, their):
        if isinstance(their, self.__class__):
            return self.__class__(self._value + their._value)
        if isinstance(their, tuple):
            return self.__class__(self._value + their)
        raise InvalidValueType((self.__class__, tuple))

    def _value_sanitize(self, value):
        if issubclass(value.__class__, ObjectIdentifier):
            return value._value
        if isinstance(value, string_types):
            try:
                value = tuple(int(arc) for arc in value.split("."))
            except ValueError:
                raise InvalidOID("unacceptable arcs values")
        if isinstance(value, tuple):
            if len(value) < 2:
                raise InvalidOID("less than 2 arcs")
            first_arc = value[0]
            if first_arc in (0, 1):
                if not (0 <= value[1] <= 39):
                    raise InvalidOID("second arc is too wide")
            elif first_arc == 2:
                pass
            else:
                raise InvalidOID("unacceptable first arc value")
            return value
        raise InvalidValueType((self.__class__, str, tuple))

    @property
    def ready(self):
        return self._value is not None

    def copy(self):
        obj = self.__class__()
        obj._value = self._value
        obj.defines = self.defines
        obj.tag = self.tag
        obj._expl = self._expl
        obj.default = self.default
        obj.optional = self.optional
        obj.offset = self.offset
        obj.llen = self.llen
        obj.vlen = self.vlen
        return obj

    def __iter__(self):
        self._assert_ready()
        return iter(self._value)

    def __str__(self):
        return ".".join(str(arc) for arc in self._value or ())

    def __hash__(self):
        self._assert_ready()
        return hash(
            self.tag +
            bytes(self._expl or b"") +
            str(self._value).encode("ascii"),
        )

    def __eq__(self, their):
        if isinstance(their, tuple):
            return self._value == their
        if not issubclass(their.__class__, ObjectIdentifier):
            return False
        return (
            self.tag == their.tag and
            self._expl == their._expl and
            self._value == their._value
        )

    def __lt__(self, their):
        return self._value < their._value

    def __call__(
            self,
            value=None,
            defines=None,
            impl=None,
            expl=None,
            default=None,
            optional=None,
    ):
        return self.__class__(
            value=value,
            defines=self.defines if defines is None else defines,
            impl=self.tag if impl is None else impl,
            expl=self._expl if expl is None else expl,
            default=self.default if default is None else default,
            optional=self.optional if optional is None else optional,
        )

    def _encode(self):
        self._assert_ready()
        value = self._value
        first_value = value[1]
        first_arc = value[0]
        if first_arc == 0:
            pass
        elif first_arc == 1:
            first_value += 40
        elif first_arc == 2:
            first_value += 80
        else:  # pragma: no cover
            raise RuntimeError("invalid arc is stored")
        octets = [zero_ended_encode(first_value)]
        for arc in value[2:]:
            octets.append(zero_ended_encode(arc))
        v = b"".join(octets)
        return b"".join((self.tag, len_encode(len(v)), v))

    def _decode(self, tlv, offset=0, decode_path=(), defines_by_path=None):
        try:
            t, _, lv = tag_strip(tlv)
        except DecodeError as err:
            raise err.__class__(
                msg=err.msg,
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        if t != self.tag:
            raise TagMismatch(
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        try:
            l, llen, v = len_decode(lv)
        except DecodeError as err:
            raise err.__class__(
                msg=err.msg,
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        if l > len(v):
            raise NotEnoughData(
                "encoded length is longer than data",
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        if l == 0:
            raise NotEnoughData(
                "zero length",
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        v, tail = v[:l], v[l:]
        arcs = []
        while len(v) > 0:
            i = 0
            arc = 0
            while True:
                octet = indexbytes(v, i)
                arc = (arc << 7) | (octet & 0x7F)
                if octet & 0x80 == 0:
                    arcs.append(arc)
                    v = v[i + 1:]
                    break
                i += 1
                if i == len(v):
                    raise DecodeError(
                        "unfinished OID",
                        klass=self.__class__,
                        decode_path=decode_path,
                        offset=offset,
                    )
        first_arc = 0
        second_arc = arcs[0]
        if 0 <= second_arc <= 39:
            first_arc = 0
        elif 40 <= second_arc <= 79:
            first_arc = 1
            second_arc -= 40
        else:
            first_arc = 2
            second_arc -= 80
        obj = self.__class__(
            value=tuple([first_arc, second_arc] + arcs[1:]),
            impl=self.tag,
            expl=self._expl,
            default=self.default,
            optional=self.optional,
            _decoded=(offset, llen, l),
        )
        return obj, tail

    def __repr__(self):
        return pp_console_row(next(self.pps()))

    def pps(self, decode_path=()):
        yield _pp(
            asn1_type_name=self.asn1_type_name,
            obj_name=self.__class__.__name__,
            decode_path=decode_path,
            value=str(self) if self.ready else None,
            optional=self.optional,
            default=self == self.default,
            impl=None if self.tag == self.tag_default else tag_decode(self.tag),
            expl=None if self._expl is None else tag_decode(self._expl),
            offset=self.offset,
            tlen=self.tlen,
            llen=self.llen,
            vlen=self.vlen,
            expl_offset=self.expl_offset if self.expled else None,
            expl_tlen=self.expl_tlen if self.expled else None,
            expl_llen=self.expl_llen if self.expled else None,
            expl_vlen=self.expl_vlen if self.expled else None,
        )


class Enumerated(Integer):
    """``ENUMERATED`` integer type

    This type is identical to :py:class:`pyderasn.Integer`, but requires
    schema to be specified and does not accept values missing from it.
    """
    __slots__ = ()
    tag_default = tag_encode(10)
    asn1_type_name = "ENUMERATED"

    def __init__(
            self,
            value=None,
            impl=None,
            expl=None,
            default=None,
            optional=False,
            _specs=None,
            _decoded=(0, 0, 0),
            bounds=None,  # dummy argument, workability for Integer.decode
    ):
        super(Enumerated, self).__init__(
            value=value,
            impl=impl,
            expl=expl,
            default=default,
            optional=optional,
            _specs=_specs,
            _decoded=_decoded,
        )
        if len(self.specs) == 0:
            raise ValueError("schema must be specified")

    def _value_sanitize(self, value):
        if isinstance(value, self.__class__):
            value = value._value
        elif isinstance(value, integer_types):
            if value not in list(self.specs.values()):
                raise DecodeError(
                    "unknown integer value: %s" % value,
                    klass=self.__class__,
                )
        elif isinstance(value, string_types):
            value = self.specs.get(value)
            if value is None:
                raise ObjUnknown("integer value: %s" % value)
        else:
            raise InvalidValueType((self.__class__, int, str))
        return value

    def copy(self):
        obj = self.__class__(_specs=self.specs)
        obj._value = self._value
        obj._bound_min = self._bound_min
        obj._bound_max = self._bound_max
        obj.tag = self.tag
        obj._expl = self._expl
        obj.default = self.default
        obj.optional = self.optional
        obj.offset = self.offset
        obj.llen = self.llen
        obj.vlen = self.vlen
        return obj

    def __call__(
            self,
            value=None,
            impl=None,
            expl=None,
            default=None,
            optional=None,
            _specs=None,
    ):
        return self.__class__(
            value=value,
            impl=self.tag if impl is None else impl,
            expl=self._expl if expl is None else expl,
            default=self.default if default is None else default,
            optional=self.optional if optional is None else optional,
            _specs=self.specs,
        )


class CommonString(OctetString):
    """Common class for all strings

    Everything resembles :py:class:`pyderasn.OctetString`, except
    ability to deal with unicode text strings.

    >>> hexenc("привет мир".encode("utf-8"))
    'd0bfd180d0b8d0b2d0b5d18220d0bcd0b8d180'
    >>> UTF8String("привет мир") == UTF8String(hexdec("d0...80"))
    True
    >>> s = UTF8String("привет мир")
    UTF8String UTF8String привет мир
    >>> str(s)
    'привет мир'
    >>> hexenc(bytes(s))
    'd0bfd180d0b8d0b2d0b5d18220d0bcd0b8d180'

    >>> PrintableString("привет мир")
    Traceback (most recent call last):
    UnicodeEncodeError: 'ascii' codec can't encode characters in position 0-5: ordinal not in range(128)

    >>> BMPString("ада", bounds=(2, 2))
    Traceback (most recent call last):
    pyderasn.BoundsError: unsatisfied bounds: 2 <= 3 <= 2
    >>> s = BMPString("ад", bounds=(2, 2))
    >>> s.encoding
    'utf-16-be'
    >>> hexenc(bytes(s))
    '04300434'

    .. list-table::
       :header-rows: 1

       * - Class
         - Text Encoding
       * - :py:class:`pyderasn.UTF8String`
         - utf-8
       * - :py:class:`pyderasn.NumericString`
         - ascii
       * - :py:class:`pyderasn.PrintableString`
         - ascii
       * - :py:class:`pyderasn.TeletexString`
         - ascii
       * - :py:class:`pyderasn.T61String`
         - ascii
       * - :py:class:`pyderasn.VideotexString`
         - iso-8859-1
       * - :py:class:`pyderasn.IA5String`
         - ascii
       * - :py:class:`pyderasn.GraphicString`
         - iso-8859-1
       * - :py:class:`pyderasn.VisibleString`
         - ascii
       * - :py:class:`pyderasn.ISO646String`
         - ascii
       * - :py:class:`pyderasn.GeneralString`
         - iso-8859-1
       * - :py:class:`pyderasn.UniversalString`
         - utf-32-be
       * - :py:class:`pyderasn.BMPString`
         - utf-16-be
    """
    __slots__ = ("encoding",)

    def _value_sanitize(self, value):
        value_raw = None
        value_decoded = None
        if isinstance(value, self.__class__):
            value_raw = value._value
        elif isinstance(value, text_type):
            value_decoded = value
        elif isinstance(value, binary_type):
            value_raw = value
        else:
            raise InvalidValueType((self.__class__, text_type, binary_type))
        value_raw = (
            value_decoded.encode(self.encoding)
            if value_raw is None else value_raw
        )
        value_decoded = (
            value_raw.decode(self.encoding)
            if value_decoded is None else value_decoded
        )
        if not self._bound_min <= len(value_decoded) <= self._bound_max:
            raise BoundsError(
                self._bound_min,
                len(value_decoded),
                self._bound_max,
            )
        return value_raw

    def __eq__(self, their):
        if isinstance(their, binary_type):
            return self._value == their
        if isinstance(their, text_type):
            return self._value == their.encode(self.encoding)
        if not isinstance(their, self.__class__):
            return False
        return (
            self._value == their._value and
            self.tag == their.tag and
            self._expl == their._expl
        )

    def __unicode__(self):
        if self.ready:
            return self._value.decode(self.encoding)
        return text_type(self._value)

    def __repr__(self):
        return pp_console_row(next(self.pps(no_unicode=PY2)))

    def pps(self, decode_path=(), no_unicode=False):
        value = None
        if self.ready:
            value = hexenc(bytes(self)) if no_unicode else self.__unicode__()
        yield _pp(
            asn1_type_name=self.asn1_type_name,
            obj_name=self.__class__.__name__,
            decode_path=decode_path,
            value=value,
            optional=self.optional,
            default=self == self.default,
            impl=None if self.tag == self.tag_default else tag_decode(self.tag),
            expl=None if self._expl is None else tag_decode(self._expl),
            offset=self.offset,
            tlen=self.tlen,
            llen=self.llen,
            vlen=self.vlen,
        )


class UTF8String(CommonString):
    __slots__ = ()
    tag_default = tag_encode(12)
    encoding = "utf-8"
    asn1_type_name = "UTF8String"


class NumericString(CommonString):
    __slots__ = ()
    tag_default = tag_encode(18)
    encoding = "ascii"
    asn1_type_name = "NumericString"


class PrintableString(CommonString):
    __slots__ = ()
    tag_default = tag_encode(19)
    encoding = "ascii"
    asn1_type_name = "PrintableString"


class TeletexString(CommonString):
    __slots__ = ()
    tag_default = tag_encode(20)
    encoding = "ascii"
    asn1_type_name = "TeletexString"


class T61String(TeletexString):
    __slots__ = ()
    asn1_type_name = "T61String"


class VideotexString(CommonString):
    __slots__ = ()
    tag_default = tag_encode(21)
    encoding = "iso-8859-1"
    asn1_type_name = "VideotexString"


class IA5String(CommonString):
    __slots__ = ()
    tag_default = tag_encode(22)
    encoding = "ascii"
    asn1_type_name = "IA5"


LEN_YYMMDDHHMMSSZ = len("YYMMDDHHMMSSZ")
LEN_YYYYMMDDHHMMSSDMZ = len("YYYYMMDDHHMMSSDMZ")
LEN_YYYYMMDDHHMMSSZ = len("YYYYMMDDHHMMSSZ")


class UTCTime(CommonString):
    """``UTCTime`` datetime type

    >>> t = UTCTime(datetime(2017, 9, 30, 22, 7, 50, 123))
    UTCTime UTCTime 2017-09-30T22:07:50
    >>> str(t)
    '170930220750Z'
    >>> bytes(t)
    b'170930220750Z'
    >>> t.todatetime()
    datetime.datetime(2017, 9, 30, 22, 7, 50)
    >>> UTCTime(datetime(2057, 9, 30, 22, 7, 50)).todatetime()
    datetime.datetime(1957, 9, 30, 22, 7, 50)
    """
    __slots__ = ()
    tag_default = tag_encode(23)
    encoding = "ascii"
    asn1_type_name = "UTCTime"

    fmt = "%y%m%d%H%M%SZ"

    def __init__(
            self,
            value=None,
            impl=None,
            expl=None,
            default=None,
            optional=False,
            _decoded=(0, 0, 0),
            bounds=None,  # dummy argument, workability for OctetString.decode
    ):
        """
        :param value: set the value. Either datetime type, or
                      :py:class:`pyderasn.UTCTime` object
        :param bytes impl: override default tag with ``IMPLICIT`` one
        :param bytes expl: override default tag with ``EXPLICIT`` one
        :param default: set default value. Type same as in ``value``
        :param bool optional: is object ``OPTIONAL`` in sequence
        """
        super(UTCTime, self).__init__(
            impl=impl,
            expl=expl,
            default=default,
            optional=optional,
            _decoded=_decoded,
        )
        self._value = value
        if value is not None:
            self._value = self._value_sanitize(value)
        if default is not None:
            default = self._value_sanitize(default)
            self.default = self.__class__(
                value=default,
                impl=self.tag,
                expl=self._expl,
            )
            if self._value is None:
                self._value = default

    def _value_sanitize(self, value):
        if isinstance(value, self.__class__):
            return value._value
        if isinstance(value, datetime):
            return value.strftime(self.fmt).encode("ascii")
        if isinstance(value, binary_type):
            value_decoded = value.decode("ascii")
            if len(value_decoded) == LEN_YYMMDDHHMMSSZ:
                try:
                    datetime.strptime(value_decoded, self.fmt)
                except ValueError:
                    raise DecodeError("invalid UTCTime format")
                return value
            else:
                raise DecodeError("invalid UTCTime length")
        raise InvalidValueType((self.__class__, datetime))

    def __eq__(self, their):
        if isinstance(their, binary_type):
            return self._value == their
        if isinstance(their, datetime):
            return self.todatetime() == their
        if not isinstance(their, self.__class__):
            return False
        return (
            self._value == their._value and
            self.tag == their.tag and
            self._expl == their._expl
        )

    def todatetime(self):
        """Convert to datetime

        :returns: datetime

        Pay attention that UTCTime can not hold full year, so all years
        having < 50 years are treated as 20xx, 19xx otherwise, according
        to X.509 recomendation.
        """
        value = datetime.strptime(self._value.decode("ascii"), self.fmt)
        year = value.year % 100
        return datetime(
            year=(2000 + year) if year < 50 else (1900 + year),
            month=value.month,
            day=value.day,
            hour=value.hour,
            minute=value.minute,
            second=value.second,
        )

    def __repr__(self):
        return pp_console_row(next(self.pps()))

    def pps(self, decode_path=()):
        yield _pp(
            asn1_type_name=self.asn1_type_name,
            obj_name=self.__class__.__name__,
            decode_path=decode_path,
            value=self.todatetime().isoformat() if self.ready else None,
            optional=self.optional,
            default=self == self.default,
            impl=None if self.tag == self.tag_default else tag_decode(self.tag),
            expl=None if self._expl is None else tag_decode(self._expl),
            offset=self.offset,
            tlen=self.tlen,
            llen=self.llen,
            vlen=self.vlen,
        )


class GeneralizedTime(UTCTime):
    """``GeneralizedTime`` datetime type

    This type is similar to :py:class:`pyderasn.UTCTime`.

    >>> t = GeneralizedTime(datetime(2017, 9, 30, 22, 7, 50, 123))
    GeneralizedTime GeneralizedTime 2017-09-30T22:07:50.000123
    >>> str(t)
    '20170930220750.000123Z'
    >>> t = GeneralizedTime(datetime(2057, 9, 30, 22, 7, 50))
    GeneralizedTime GeneralizedTime 2057-09-30T22:07:50
    """
    __slots__ = ()
    tag_default = tag_encode(24)
    asn1_type_name = "GeneralizedTime"

    fmt = "%Y%m%d%H%M%SZ"
    fmt_ms = "%Y%m%d%H%M%S.%fZ"

    def _value_sanitize(self, value):
        if isinstance(value, self.__class__):
            return value._value
        if isinstance(value, datetime):
            return value.strftime(
                self.fmt_ms if value.microsecond > 0 else self.fmt
            ).encode("ascii")
        if isinstance(value, binary_type):
            value_decoded = value.decode("ascii")
            if len(value_decoded) == LEN_YYYYMMDDHHMMSSZ:
                try:
                    datetime.strptime(value_decoded, self.fmt)
                except ValueError:
                    raise DecodeError(
                        "invalid GeneralizedTime (without ms) format",
                    )
                return value
            elif len(value_decoded) >= LEN_YYYYMMDDHHMMSSDMZ:
                try:
                    datetime.strptime(value_decoded, self.fmt_ms)
                except ValueError:
                    raise DecodeError(
                        "invalid GeneralizedTime (with ms) format",
                    )
                return value
            else:
                raise DecodeError(
                    "invalid GeneralizedTime length",
                    klass=self.__class__,
                )
        raise InvalidValueType((self.__class__, datetime))

    def todatetime(self):
        value = self._value.decode("ascii")
        if len(value) == LEN_YYYYMMDDHHMMSSZ:
            return datetime.strptime(value, self.fmt)
        return datetime.strptime(value, self.fmt_ms)


class GraphicString(CommonString):
    __slots__ = ()
    tag_default = tag_encode(25)
    encoding = "iso-8859-1"
    asn1_type_name = "GraphicString"


class VisibleString(CommonString):
    __slots__ = ()
    tag_default = tag_encode(26)
    encoding = "ascii"
    asn1_type_name = "VisibleString"


class ISO646String(VisibleString):
    __slots__ = ()
    asn1_type_name = "ISO646String"


class GeneralString(CommonString):
    __slots__ = ()
    tag_default = tag_encode(27)
    encoding = "iso-8859-1"
    asn1_type_name = "GeneralString"


class UniversalString(CommonString):
    __slots__ = ()
    tag_default = tag_encode(28)
    encoding = "utf-32-be"
    asn1_type_name = "UniversalString"


class BMPString(CommonString):
    __slots__ = ()
    tag_default = tag_encode(30)
    encoding = "utf-16-be"
    asn1_type_name = "BMPString"


class Choice(Obj):
    """``CHOICE`` special type

    ::

        class GeneralName(Choice):
            schema = (
                ('rfc822Name', IA5String(impl=tag_ctxp(1))),
                ('dNSName', IA5String(impl=tag_ctxp(2))),
            )

    >>> gn = GeneralName()
    GeneralName CHOICE
    >>> gn["rfc822Name"] = IA5String("foo@bar.baz")
    GeneralName CHOICE rfc822Name[[1] IA5String IA5 foo@bar.baz]
    >>> gn["dNSName"] = IA5String("bar.baz")
    GeneralName CHOICE dNSName[[2] IA5String IA5 bar.baz]
    >>> gn["rfc822Name"]
    None
    >>> gn["dNSName"]
    [2] IA5String IA5 bar.baz
    >>> gn.choice
    'dNSName'
    >>> gn.value == gn["dNSName"]
    True
    >>> gn.specs
    OrderedDict([('rfc822Name', [1] IA5String IA5), ('dNSName', [2] IA5String IA5)])

    >>> GeneralName(("rfc822Name", IA5String("foo@bar.baz")))
    GeneralName CHOICE rfc822Name[[1] IA5String IA5 foo@bar.baz]
    """
    __slots__ = ("specs",)
    tag_default = None
    asn1_type_name = "CHOICE"

    def __init__(
            self,
            value=None,
            schema=None,
            impl=None,
            expl=None,
            default=None,
            optional=False,
            _decoded=(0, 0, 0),
    ):
        """
        :param value: set the value. Either ``(choice, value)`` tuple, or
                      :py:class:`pyderasn.Choice` object
        :param bytes impl: can not be set, do **not** use it
        :param bytes expl: override default tag with ``EXPLICIT`` one
        :param default: set default value. Type same as in ``value``
        :param bool optional: is object ``OPTIONAL`` in sequence
        """
        if impl is not None:
            raise ValueError("no implicit tag allowed for CHOICE")
        super(Choice, self).__init__(None, expl, default, optional, _decoded)
        if schema is None:
            schema = getattr(self, "schema", ())
        if len(schema) == 0:
            raise ValueError("schema must be specified")
        self.specs = (
            schema if isinstance(schema, OrderedDict) else OrderedDict(schema)
        )
        self._value = None
        if value is not None:
            self._value = self._value_sanitize(value)
        if default is not None:
            default_value = self._value_sanitize(default)
            default_obj = self.__class__(impl=self.tag, expl=self._expl)
            default_obj.specs = self.specs
            default_obj._value = default_value
            self.default = default_obj
            if value is None:
                self._value = default_obj.copy()._value

    def _value_sanitize(self, value):
        if isinstance(value, self.__class__):
            return value._value
        if isinstance(value, tuple) and len(value) == 2:
            choice, obj = value
            spec = self.specs.get(choice)
            if spec is None:
                raise ObjUnknown(choice)
            if not isinstance(obj, spec.__class__):
                raise InvalidValueType((spec,))
            return (choice, spec(obj))
        raise InvalidValueType((self.__class__, tuple))

    @property
    def ready(self):
        return self._value is not None and self._value[1].ready

    def copy(self):
        obj = self.__class__(schema=self.specs)
        obj._expl = self._expl
        obj.default = self.default
        obj.optional = self.optional
        obj.offset = self.offset
        obj.llen = self.llen
        obj.vlen = self.vlen
        value = self._value
        if value is not None:
            obj._value = (value[0], value[1].copy())
        return obj

    def __eq__(self, their):
        if isinstance(their, tuple) and len(their) == 2:
            return self._value == their
        if not isinstance(their, self.__class__):
            return False
        return (
            self.specs == their.specs and
            self._value == their._value
        )

    def __call__(
            self,
            value=None,
            expl=None,
            default=None,
            optional=None,
    ):
        return self.__class__(
            value=value,
            schema=self.specs,
            expl=self._expl if expl is None else expl,
            default=self.default if default is None else default,
            optional=self.optional if optional is None else optional,
        )

    @property
    def choice(self):
        self._assert_ready()
        return self._value[0]

    @property
    def value(self):
        self._assert_ready()
        return self._value[1]

    def __getitem__(self, key):
        if key not in self.specs:
            raise ObjUnknown(key)
        if self._value is None:
            return None
        choice, value = self._value
        if choice != key:
            return None
        return value

    def __setitem__(self, key, value):
        spec = self.specs.get(key)
        if spec is None:
            raise ObjUnknown(key)
        if not isinstance(value, spec.__class__):
            raise InvalidValueType((spec.__class__,))
        self._value = (key, spec(value))

    @property
    def tlen(self):
        return 0

    @property
    def decoded(self):
        return self._value[1].decoded if self.ready else False

    def _encode(self):
        self._assert_ready()
        return self._value[1].encode()

    def _decode(self, tlv, offset=0, decode_path=(), defines_by_path=None):
        for choice, spec in self.specs.items():
            try:
                value, tail = spec.decode(
                    tlv,
                    offset=offset,
                    leavemm=True,
                    decode_path=decode_path + (choice,),
                    defines_by_path=defines_by_path,
                )
            except TagMismatch:
                continue
            obj = self.__class__(
                schema=self.specs,
                expl=self._expl,
                default=self.default,
                optional=self.optional,
                _decoded=(offset, 0, value.tlvlen),
            )
            obj._value = (choice, value)
            return obj, tail
        raise TagMismatch(
            klass=self.__class__,
            decode_path=decode_path,
            offset=offset,
        )

    def __repr__(self):
        value = pp_console_row(next(self.pps()))
        if self.ready:
            value = "%s[%r]" % (value, self.value)
        return value

    def pps(self, decode_path=()):
        yield _pp(
            asn1_type_name=self.asn1_type_name,
            obj_name=self.__class__.__name__,
            decode_path=decode_path,
            value=self.choice if self.ready else None,
            optional=self.optional,
            default=self == self.default,
            impl=None if self.tag == self.tag_default else tag_decode(self.tag),
            expl=None if self._expl is None else tag_decode(self._expl),
            offset=self.offset,
            tlen=self.tlen,
            llen=self.llen,
            vlen=self.vlen,
        )
        if self.ready:
            yield self.value.pps(decode_path=decode_path + (self.choice,))


class PrimitiveTypes(Choice):
    """Predefined ``CHOICE`` for all generic primitive types

    It could be useful for general decoding of some unspecified values:

    >>> PrimitiveTypes().decode(hexdec("0403666f6f"))[0].value
    OCTET STRING 3 bytes 666f6f
    >>> PrimitiveTypes().decode(hexdec("0203123456"))[0].value
    INTEGER 1193046
    """
    __slots__ = ()
    schema = tuple((klass.__name__, klass()) for klass in (
        Boolean,
        Integer,
        BitString,
        OctetString,
        Null,
        ObjectIdentifier,
        UTF8String,
        NumericString,
        PrintableString,
        TeletexString,
        VideotexString,
        IA5String,
        UTCTime,
        GeneralizedTime,
        GraphicString,
        VisibleString,
        ISO646String,
        GeneralString,
        UniversalString,
        BMPString,
    ))


class Any(Obj):
    """``ANY`` special type

    >>> Any(Integer(-123))
    ANY 020185
    >>> a = Any(OctetString(b"hello world").encode())
    ANY 040b68656c6c6f20776f726c64
    >>> hexenc(bytes(a))
    b'0x040x0bhello world'
    """
    __slots__ = ("defined",)
    tag_default = tag_encode(0)
    asn1_type_name = "ANY"

    def __init__(
            self,
            value=None,
            expl=None,
            optional=False,
            _decoded=(0, 0, 0),
    ):
        """
        :param value: set the value. Either any kind of pyderasn's
                      **ready** object, or bytes. Pay attention that
                      **no** validation is performed is raw binary value
                      is valid TLV
        :param bytes expl: override default tag with ``EXPLICIT`` one
        :param bool optional: is object ``OPTIONAL`` in sequence
        """
        super(Any, self).__init__(None, expl, None, optional, _decoded)
        self._value = None if value is None else self._value_sanitize(value)
        self.defined = None

    def _value_sanitize(self, value):
        if isinstance(value, self.__class__):
            return value._value
        if isinstance(value, Obj):
            return value.encode()
        if isinstance(value, binary_type):
            return value
        raise InvalidValueType((self.__class__, Obj, binary_type))

    @property
    def ready(self):
        return self._value is not None

    def copy(self):
        obj = self.__class__()
        obj._value = self._value
        obj.tag = self.tag
        obj._expl = self._expl
        obj.optional = self.optional
        obj.offset = self.offset
        obj.llen = self.llen
        obj.vlen = self.vlen
        return obj

    def __eq__(self, their):
        if isinstance(their, binary_type):
            return self._value == their
        if issubclass(their.__class__, Any):
            return self._value == their._value
        return False

    def __call__(
            self,
            value=None,
            expl=None,
            optional=None,
    ):
        return self.__class__(
            value=value,
            expl=self._expl if expl is None else expl,
            optional=self.optional if optional is None else optional,
        )

    def __bytes__(self):
        self._assert_ready()
        return self._value

    @property
    def tlen(self):
        return 0

    def _encode(self):
        self._assert_ready()
        return self._value

    def _decode(self, tlv, offset=0, decode_path=(), defines_by_path=None):
        try:
            t, tlen, lv = tag_strip(tlv)
            l, llen, v = len_decode(lv)
        except DecodeError as err:
            raise err.__class__(
                msg=err.msg,
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        if l > len(v):
            raise NotEnoughData(
                "encoded length is longer than data",
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        tlvlen = tlen + llen + l
        v, tail = tlv[:tlvlen], v[l:]
        obj = self.__class__(
            value=v.tobytes(),
            expl=self._expl,
            optional=self.optional,
            _decoded=(offset, 0, tlvlen),
        )
        obj.tag = t
        return obj, tail

    def __repr__(self):
        return pp_console_row(next(self.pps()))

    def pps(self, decode_path=()):
        yield _pp(
            asn1_type_name=self.asn1_type_name,
            obj_name=self.__class__.__name__,
            decode_path=decode_path,
            blob=self._value if self.ready else None,
            optional=self.optional,
            default=self == self.default,
            impl=None if self.tag == self.tag_default else tag_decode(self.tag),
            expl=None if self._expl is None else tag_decode(self._expl),
            offset=self.offset,
            tlen=self.tlen,
            llen=self.llen,
            vlen=self.vlen,
            expl_offset=self.expl_offset if self.expled else None,
            expl_tlen=self.expl_tlen if self.expled else None,
            expl_llen=self.expl_llen if self.expled else None,
            expl_vlen=self.expl_vlen if self.expled else None,
        )
        defined_by, defined = self.defined or (None, None)
        if defined_by is not None:
            yield defined.pps(
                decode_path=decode_path + (decode_path_defby(defined_by),)
            )


########################################################################
# ASN.1 constructed types
########################################################################

def get_def_by_path(defines_by_path, sub_decode_path):
    """Get define by decode path
    """
    for path, define in defines_by_path:
        if len(path) != len(sub_decode_path):
            continue
        for p1, p2 in zip(path, sub_decode_path):
            if (p1 != any) and (p1 != p2):
                break
        else:
            return define


class Sequence(Obj):
    """``SEQUENCE`` structure type

    You have to make specification of sequence::

        class Extension(Sequence):
            schema = (
                ("extnID", ObjectIdentifier()),
                ("critical", Boolean(default=False)),
                ("extnValue", OctetString()),
            )

    Then, you can work with it as with dictionary.

    >>> ext = Extension()
    >>> Extension().specs
    OrderedDict([
        ('extnID', OBJECT IDENTIFIER),
        ('critical', BOOLEAN False OPTIONAL DEFAULT),
        ('extnValue', OCTET STRING),
    ])
    >>> ext["extnID"] = "1.2.3"
    Traceback (most recent call last):
    pyderasn.InvalidValueType: invalid value type, expected: <class 'pyderasn.ObjectIdentifier'>
    >>> ext["extnID"] = ObjectIdentifier("1.2.3")

    You can know if sequence is ready to be encoded:

    >>> ext.ready
    False
    >>> ext.encode()
    Traceback (most recent call last):
    pyderasn.ObjNotReady: object is not ready: extnValue
    >>> ext["extnValue"] = OctetString(b"foobar")
    >>> ext.ready
    True

    Value you want to assign, must have the same **type** as in
    corresponding specification, but it can have different tags,
    optional/default attributes -- they will be taken from specification
    automatically::

        class TBSCertificate(Sequence):
            schema = (
                ("version", Version(expl=tag_ctxc(0), default="v1")),
            [...]

    >>> tbs = TBSCertificate()
    >>> tbs["version"] = Version("v2") # no need to explicitly add ``expl``

    You can know if value exists/set in the sequence and take its value:

    >>> "extnID" in ext, "extnValue" in ext, "critical" in ext
    (True, True, False)
    >>> ext["extnID"]
    OBJECT IDENTIFIER 1.2.3

    But pay attention that if value has default, then it won't be (not
    in) in the sequence (because ``DEFAULT`` must not be encoded in
    DER), but you can read its value:

    >>> "critical" in ext, ext["critical"]
    (False, BOOLEAN False)
    >>> ext["critical"] = Boolean(True)
    >>> "critical" in ext, ext["critical"]
    (True, BOOLEAN True)

    All defaulted values are always optional.

    .. warning::

       When decoded DER contains defaulted value inside, then
       technically this is not valid DER encoding. But we allow
       and pass it. Of course reencoding of that kind of DER will
       result in different binary representation (validly without
       defaulted value inside).

    Two sequences are equal if they have equal specification (schema),
    implicit/explicit tagging and the same values.
    """
    __slots__ = ("specs",)
    tag_default = tag_encode(form=TagFormConstructed, num=16)
    asn1_type_name = "SEQUENCE"

    def __init__(
            self,
            value=None,
            schema=None,
            impl=None,
            expl=None,
            default=None,
            optional=False,
            _decoded=(0, 0, 0),
    ):
        super(Sequence, self).__init__(impl, expl, default, optional, _decoded)
        if schema is None:
            schema = getattr(self, "schema", ())
        self.specs = (
            schema if isinstance(schema, OrderedDict) else OrderedDict(schema)
        )
        self._value = {}
        if value is not None:
            self._value = self._value_sanitize(value)
        if default is not None:
            default_value = self._value_sanitize(default)
            default_obj = self.__class__(impl=self.tag, expl=self._expl)
            default_obj.specs = self.specs
            default_obj._value = default_value
            self.default = default_obj
            if value is None:
                self._value = default_obj.copy()._value

    def _value_sanitize(self, value):
        if not issubclass(value.__class__, Sequence):
            raise InvalidValueType((Sequence,))
        return value._value

    @property
    def ready(self):
        for name, spec in self.specs.items():
            value = self._value.get(name)
            if value is None:
                if spec.optional:
                    continue
                return False
            else:
                if not value.ready:
                    return False
        return True

    def copy(self):
        obj = self.__class__(schema=self.specs)
        obj.tag = self.tag
        obj._expl = self._expl
        obj.default = self.default
        obj.optional = self.optional
        obj.offset = self.offset
        obj.llen = self.llen
        obj.vlen = self.vlen
        obj._value = {k: v.copy() for k, v in self._value.items()}
        return obj

    def __eq__(self, their):
        if not isinstance(their, self.__class__):
            return False
        return (
            self.specs == their.specs and
            self.tag == their.tag and
            self._expl == their._expl and
            self._value == their._value
        )

    def __call__(
            self,
            value=None,
            impl=None,
            expl=None,
            default=None,
            optional=None,
    ):
        return self.__class__(
            value=value,
            schema=self.specs,
            impl=self.tag if impl is None else impl,
            expl=self._expl if expl is None else expl,
            default=self.default if default is None else default,
            optional=self.optional if optional is None else optional,
        )

    def __contains__(self, key):
        return key in self._value

    def __setitem__(self, key, value):
        spec = self.specs.get(key)
        if spec is None:
            raise ObjUnknown(key)
        if value is None:
            self._value.pop(key, None)
            return
        if not isinstance(value, spec.__class__):
            raise InvalidValueType((spec.__class__,))
        value = spec(value=value)
        if spec.default is not None and value == spec.default:
            self._value.pop(key, None)
            return
        self._value[key] = value

    def __getitem__(self, key):
        value = self._value.get(key)
        if value is not None:
            return value
        spec = self.specs.get(key)
        if spec is None:
            raise ObjUnknown(key)
        if spec.default is not None:
            return spec.default
        return None

    def _encoded_values(self):
        raws = []
        for name, spec in self.specs.items():
            value = self._value.get(name)
            if value is None:
                if spec.optional:
                    continue
                raise ObjNotReady(name)
            raws.append(value.encode())
        return raws

    def _encode(self):
        v = b"".join(self._encoded_values())
        return b"".join((self.tag, len_encode(len(v)), v))

    def _decode(self, tlv, offset=0, decode_path=(), defines_by_path=None):
        try:
            t, tlen, lv = tag_strip(tlv)
        except DecodeError as err:
            raise err.__class__(
                msg=err.msg,
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        if t != self.tag:
            raise TagMismatch(
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        try:
            l, llen, v = len_decode(lv)
        except DecodeError as err:
            raise err.__class__(
                msg=err.msg,
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        if l > len(v):
            raise NotEnoughData(
                "encoded length is longer than data",
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        v, tail = v[:l], v[l:]
        sub_offset = offset + tlen + llen
        values = {}
        defines = {}
        for name, spec in self.specs.items():
            if len(v) == 0 and spec.optional:
                continue
            sub_decode_path = decode_path + (name,)
            try:
                value, v_tail = spec.decode(
                    v,
                    sub_offset,
                    leavemm=True,
                    decode_path=sub_decode_path,
                    defines_by_path=defines_by_path,
                )
            except TagMismatch:
                if spec.optional:
                    continue
                raise

            defined = defines.pop(name, None)
            if defined is not None:
                defined_by, defined_spec = defined
                if issubclass(value.__class__, SequenceOf):
                    for i, _value in enumerate(value):
                        sub_sub_decode_path = sub_decode_path + (
                            str(i),
                            decode_path_defby(defined_by),
                        )
                        defined_value, defined_tail = defined_spec.decode(
                            memoryview(bytes(_value)),
                            sub_offset + value.tlen + value.llen,
                            leavemm=True,
                            decode_path=sub_sub_decode_path,
                            defines_by_path=defines_by_path,
                        )
                        if len(defined_tail) > 0:
                            raise DecodeError(
                                "remaining data",
                                klass=self.__class__,
                                decode_path=sub_sub_decode_path,
                                offset=offset,
                            )
                        _value.defined = (defined_by, defined_value)
                else:
                    defined_value, defined_tail = defined_spec.decode(
                        memoryview(bytes(value)),
                        sub_offset + value.tlen + value.llen,
                        leavemm=True,
                        decode_path=sub_decode_path + (decode_path_defby(defined_by),),
                        defines_by_path=defines_by_path,
                    )
                    if len(defined_tail) > 0:
                        raise DecodeError(
                            "remaining data",
                            klass=self.__class__,
                            decode_path=sub_decode_path + (decode_path_defby(defined_by),),
                            offset=offset,
                        )
                    value.defined = (defined_by, defined_value)

            sub_offset += (value.expl_tlvlen if value.expled else value.tlvlen)
            v = v_tail
            if spec.default is not None and value == spec.default:
                # Encoded default values are not valid in DER,
                # but we allow that anyway
                continue
            values[name] = value

            spec_defines = getattr(spec, "defines", None)
            if defines_by_path is not None and spec_defines is None:
                spec_defines = get_def_by_path(defines_by_path, sub_decode_path)
            if spec_defines is not None:
                what, schema = spec_defines
                defined = schema.get(value, None)
                if defined is not None:
                    defines[what] = (value, defined)
        if len(v) > 0:
            raise DecodeError(
                "remaining data",
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        obj = self.__class__(
            schema=self.specs,
            impl=self.tag,
            expl=self._expl,
            default=self.default,
            optional=self.optional,
            _decoded=(offset, llen, l),
        )
        obj._value = values
        return obj, tail

    def __repr__(self):
        value = pp_console_row(next(self.pps()))
        cols = []
        for name in self.specs:
            _value = self._value.get(name)
            if _value is None:
                continue
            cols.append(repr(_value))
        return "%s[%s]" % (value, ", ".join(cols))

    def pps(self, decode_path=()):
        yield _pp(
            asn1_type_name=self.asn1_type_name,
            obj_name=self.__class__.__name__,
            decode_path=decode_path,
            optional=self.optional,
            default=self == self.default,
            impl=None if self.tag == self.tag_default else tag_decode(self.tag),
            expl=None if self._expl is None else tag_decode(self._expl),
            offset=self.offset,
            tlen=self.tlen,
            llen=self.llen,
            vlen=self.vlen,
            expl_offset=self.expl_offset if self.expled else None,
            expl_tlen=self.expl_tlen if self.expled else None,
            expl_llen=self.expl_llen if self.expled else None,
            expl_vlen=self.expl_vlen if self.expled else None,
        )
        for name in self.specs:
            value = self._value.get(name)
            if value is None:
                continue
            yield value.pps(decode_path=decode_path + (name,))


class Set(Sequence):
    """``SET`` structure type

    Its usage is identical to :py:class:`pyderasn.Sequence`.
    """
    __slots__ = ()
    tag_default = tag_encode(form=TagFormConstructed, num=17)
    asn1_type_name = "SET"

    def _encode(self):
        raws = self._encoded_values()
        raws.sort()
        v = b"".join(raws)
        return b"".join((self.tag, len_encode(len(v)), v))

    def _decode(self, tlv, offset=0, decode_path=(), defines_by_path=None):
        try:
            t, tlen, lv = tag_strip(tlv)
        except DecodeError as err:
            raise err.__class__(
                msg=err.msg,
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        if t != self.tag:
            raise TagMismatch(
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        try:
            l, llen, v = len_decode(lv)
        except DecodeError as err:
            raise err.__class__(
                msg=err.msg,
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        if l > len(v):
            raise NotEnoughData(
                "encoded length is longer than data",
                klass=self.__class__,
                offset=offset,
            )
        v, tail = v[:l], v[l:]
        sub_offset = offset + tlen + llen
        values = {}
        specs_items = self.specs.items
        while len(v) > 0:
            for name, spec in specs_items():
                try:
                    value, v_tail = spec.decode(
                        v,
                        sub_offset,
                        leavemm=True,
                        decode_path=decode_path + (name,),
                        defines_by_path=defines_by_path,
                    )
                except TagMismatch:
                    continue
                sub_offset += (
                    value.expl_tlvlen if value.expled else value.tlvlen
                )
                v = v_tail
                if spec.default is None or value != spec.default:  # pragma: no cover
                    # SeqMixing.test_encoded_default_accepted covers that place
                    values[name] = value
                break
            else:
                raise TagMismatch(
                    klass=self.__class__,
                    decode_path=decode_path,
                    offset=offset,
                )
        obj = self.__class__(
            schema=self.specs,
            impl=self.tag,
            expl=self._expl,
            default=self.default,
            optional=self.optional,
            _decoded=(offset, llen, l),
        )
        obj._value = values
        return obj, tail


class SequenceOf(Obj):
    """``SEQUENCE OF`` sequence type

    For that kind of type you must specify the object it will carry on
    (bounds are for example here, not required)::

        class Ints(SequenceOf):
            schema = Integer()
            bounds = (0, 2)

    >>> ints = Ints()
    >>> ints.append(Integer(123))
    >>> ints.append(Integer(234))
    >>> ints
    Ints SEQUENCE OF[INTEGER 123, INTEGER 234]
    >>> [int(i) for i in ints]
    [123, 234]
    >>> ints.append(Integer(345))
    Traceback (most recent call last):
    pyderasn.BoundsError: unsatisfied bounds: 0 <= 3 <= 2
    >>> ints[1]
    INTEGER 234
    >>> ints[1] = Integer(345)
    >>> ints
    Ints SEQUENCE OF[INTEGER 123, INTEGER 345]

    Also you can initialize sequence with preinitialized values:

    >>> ints = Ints([Integer(123), Integer(234)])
    """
    __slots__ = ("spec", "_bound_min", "_bound_max")
    tag_default = tag_encode(form=TagFormConstructed, num=16)
    asn1_type_name = "SEQUENCE OF"

    def __init__(
            self,
            value=None,
            schema=None,
            bounds=None,
            impl=None,
            expl=None,
            default=None,
            optional=False,
            _decoded=(0, 0, 0),
    ):
        super(SequenceOf, self).__init__(
            impl,
            expl,
            default,
            optional,
            _decoded,
        )
        if schema is None:
            schema = getattr(self, "schema", None)
        if schema is None:
            raise ValueError("schema must be specified")
        self.spec = schema
        self._bound_min, self._bound_max = getattr(
            self,
            "bounds",
            (0, float("+inf")),
        ) if bounds is None else bounds
        self._value = []
        if value is not None:
            self._value = self._value_sanitize(value)
        if default is not None:
            default_value = self._value_sanitize(default)
            default_obj = self.__class__(
                schema=schema,
                impl=self.tag,
                expl=self._expl,
            )
            default_obj._value = default_value
            self.default = default_obj
            if value is None:
                self._value = default_obj.copy()._value

    def _value_sanitize(self, value):
        if issubclass(value.__class__, SequenceOf):
            value = value._value
        elif hasattr(value, "__iter__"):
            value = list(value)
        else:
            raise InvalidValueType((self.__class__, iter))
        if not self._bound_min <= len(value) <= self._bound_max:
            raise BoundsError(self._bound_min, len(value), self._bound_max)
        for v in value:
            if not isinstance(v, self.spec.__class__):
                raise InvalidValueType((self.spec.__class__,))
        return value

    @property
    def ready(self):
        return all(v.ready for v in self._value)

    def copy(self):
        obj = self.__class__(schema=self.spec)
        obj._bound_min = self._bound_min
        obj._bound_max = self._bound_max
        obj.tag = self.tag
        obj._expl = self._expl
        obj.default = self.default
        obj.optional = self.optional
        obj.offset = self.offset
        obj.llen = self.llen
        obj.vlen = self.vlen
        obj._value = [v.copy() for v in self._value]
        return obj

    def __eq__(self, their):
        if isinstance(their, self.__class__):
            return (
                self.spec == their.spec and
                self.tag == their.tag and
                self._expl == their._expl and
                self._value == their._value
            )
        if hasattr(their, "__iter__"):
            return self._value == list(their)
        return False

    def __call__(
            self,
            value=None,
            bounds=None,
            impl=None,
            expl=None,
            default=None,
            optional=None,
    ):
        return self.__class__(
            value=value,
            schema=self.spec,
            bounds=(
                (self._bound_min, self._bound_max)
                if bounds is None else bounds
            ),
            impl=self.tag if impl is None else impl,
            expl=self._expl if expl is None else expl,
            default=self.default if default is None else default,
            optional=self.optional if optional is None else optional,
        )

    def __contains__(self, key):
        return key in self._value

    def append(self, value):
        if not isinstance(value, self.spec.__class__):
            raise InvalidValueType((self.spec.__class__,))
        if len(self._value) + 1 > self._bound_max:
            raise BoundsError(
                self._bound_min,
                len(self._value) + 1,
                self._bound_max,
            )
        self._value.append(value)

    def __iter__(self):
        self._assert_ready()
        return iter(self._value)

    def __len__(self):
        self._assert_ready()
        return len(self._value)

    def __setitem__(self, key, value):
        if not isinstance(value, self.spec.__class__):
            raise InvalidValueType((self.spec.__class__,))
        self._value[key] = self.spec(value=value)

    def __getitem__(self, key):
        return self._value[key]

    def _encoded_values(self):
        return [v.encode() for v in self._value]

    def _encode(self):
        v = b"".join(self._encoded_values())
        return b"".join((self.tag, len_encode(len(v)), v))

    def _decode(self, tlv, offset=0, decode_path=(), defines_by_path=None):
        try:
            t, tlen, lv = tag_strip(tlv)
        except DecodeError as err:
            raise err.__class__(
                msg=err.msg,
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        if t != self.tag:
            raise TagMismatch(
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        try:
            l, llen, v = len_decode(lv)
        except DecodeError as err:
            raise err.__class__(
                msg=err.msg,
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        if l > len(v):
            raise NotEnoughData(
                "encoded length is longer than data",
                klass=self.__class__,
                decode_path=decode_path,
                offset=offset,
            )
        v, tail = v[:l], v[l:]
        sub_offset = offset + tlen + llen
        _value = []
        spec = self.spec
        while len(v) > 0:
            value, v_tail = spec.decode(
                v,
                sub_offset,
                leavemm=True,
                decode_path=decode_path + (str(len(_value)),),
                defines_by_path=defines_by_path,
            )
            sub_offset += (value.expl_tlvlen if value.expled else value.tlvlen)
            v = v_tail
            _value.append(value)
        obj = self.__class__(
            value=_value,
            schema=spec,
            bounds=(self._bound_min, self._bound_max),
            impl=self.tag,
            expl=self._expl,
            default=self.default,
            optional=self.optional,
            _decoded=(offset, llen, l),
        )
        return obj, tail

    def __repr__(self):
        return "%s[%s]" % (
            pp_console_row(next(self.pps())),
            ", ".join(repr(v) for v in self._value),
        )

    def pps(self, decode_path=()):
        yield _pp(
            asn1_type_name=self.asn1_type_name,
            obj_name=self.__class__.__name__,
            decode_path=decode_path,
            optional=self.optional,
            default=self == self.default,
            impl=None if self.tag == self.tag_default else tag_decode(self.tag),
            expl=None if self._expl is None else tag_decode(self._expl),
            offset=self.offset,
            tlen=self.tlen,
            llen=self.llen,
            vlen=self.vlen,
            expl_offset=self.expl_offset if self.expled else None,
            expl_tlen=self.expl_tlen if self.expled else None,
            expl_llen=self.expl_llen if self.expled else None,
            expl_vlen=self.expl_vlen if self.expled else None,
        )
        for i, value in enumerate(self._value):
            yield value.pps(decode_path=decode_path + (str(i),))


class SetOf(SequenceOf):
    """``SET OF`` sequence type

    Its usage is identical to :py:class:`pyderasn.SequenceOf`.
    """
    __slots__ = ()
    tag_default = tag_encode(form=TagFormConstructed, num=17)
    asn1_type_name = "SET OF"

    def _encode(self):
        raws = self._encoded_values()
        raws.sort()
        v = b"".join(raws)
        return b"".join((self.tag, len_encode(len(v)), v))


def obj_by_path(pypath):  # pragma: no cover
    """Import object specified as string Python path

    Modules must be separated from classes/functions with ``:``.

    >>> obj_by_path("foo.bar:Baz")
    <class 'foo.bar.Baz'>
    >>> obj_by_path("foo.bar:Baz.boo")
    <classmethod 'foo.bar.Baz.boo'>
    """
    mod, objs = pypath.rsplit(":", 1)
    from importlib import import_module
    obj = import_module(mod)
    for obj_name in objs.split("."):
        obj = getattr(obj, obj_name)
    return obj


def generic_decoder():  # pragma: no cover
    # All of this below is a big hack with self references
    choice = PrimitiveTypes()
    choice.specs["SequenceOf"] = SequenceOf(schema=choice)
    choice.specs["SetOf"] = SetOf(schema=choice)
    for i in range(31):
        choice.specs["SequenceOf%d" % i] = SequenceOf(
            schema=choice,
            expl=tag_ctxc(i),
        )
    choice.specs["Any"] = Any()

    # Class name equals to type name, to omit it from output
    class SEQUENCEOF(SequenceOf):
        __slots__ = ()
        schema = choice

    def pprint_any(obj, oids=None):
        def _pprint_pps(pps):
            for pp in pps:
                if hasattr(pp, "_fields"):
                    if pp.asn1_type_name == Choice.asn1_type_name:
                        continue
                    pp_kwargs = pp._asdict()
                    pp_kwargs["decode_path"] = pp.decode_path[:-1] + (">",)
                    pp = _pp(**pp_kwargs)
                    yield pp_console_row(
                        pp,
                        oids=oids,
                        with_offsets=True,
                        with_blob=False,
                    )
                    for row in pp_console_blob(pp):
                        yield row
                else:
                    for row in _pprint_pps(pp):
                        yield row
        return "\n".join(_pprint_pps(obj.pps()))
    return SEQUENCEOF(), pprint_any


def main():  # pragma: no cover
    import argparse
    parser = argparse.ArgumentParser(description="PyDERASN ASN.1 DER decoder")
    parser.add_argument(
        "--oids",
        help="Python path to dictionary with OIDs",
    )
    parser.add_argument(
        "--schema",
        help="Python path to schema definition to use",
    )
    parser.add_argument(
        "--defines-by-path",
        help="Python path to decoder's defines_by_path",
    )
    parser.add_argument(
        "DERFile",
        type=argparse.FileType("rb"),
        help="Path to DER file you want to decode",
    )
    args = parser.parse_args()
    der = memoryview(args.DERFile.read())
    args.DERFile.close()
    oids = obj_by_path(args.oids) if args.oids else {}
    if args.schema:
        schema = obj_by_path(args.schema)
        from functools import partial
        pprinter = partial(pprint, big_blobs=True)
    else:
        schema, pprinter = generic_decoder()
    obj, tail = schema().decode(
        der,
        defines_by_path=(
            None if args.defines_by_path is None
            else obj_by_path(args.defines_by_path)
        ),
    )
    print(pprinter(obj, oids=oids))
    if tail != b"":
        print("\nTrailing data: %s" % hexenc(tail))


if __name__ == "__main__":
    main()
