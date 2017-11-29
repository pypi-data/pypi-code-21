# -*- coding: utf-8 -*-
# cython: language_level=3, always_allow_keywords=True

## Copyright 2011-2017 by LivingLogic AG, Bayreuth/Germany
## Copyright 2011-2017 by Walter Dörwald
##
## All Rights Reserved
##
## See ll/xist/__init__.py for the license


"""
This module provides functions for encoding and decoding a lightweight
text-based format for serializing the object types supported by UL4.

It is extensible to allow encoding/decoding arbitrary instances (i.e. it is
basically a reimplementation of :mod:`pickle`, but with string input/output
instead of bytes and with an eye towards cross-plattform support).

There are implementations for Python (this module), Java_ and Javascript_
(as part of the UL4 packages for those languages).

.. _Java: https://github.com/LivingLogic/LivingLogic.Java.ul4
.. _Javascript: https://github.com/LivingLogic/LivingLogic.Javascript.ul4

Furthermore there's an `Oracle package`_ that can be used for generating
UL4ON encoded data.

.. _Oracle package: https://github.com/LivingLogic/LivingLogic.Oracle.ul4

Basic usage follows the API design of :mod:`pickle`, :mod:`json`, etc. and
supports most builtin Python types::

	>>> from ll import ul4on
	>>> ul4on.dumps(None)
	'n'
	>>> ul4on.loads('n')
	>>> ul4on.dumps(False)
	'bF'
	>>> ul4on.loads('bF')
	False
	>>> ul4on.dumps(42)
	'i42'
	>>> ul4on.loads('i42')
	42
	>>> ul4on.dumps(42.5)
	'f42.5'
	>>> ul4on.loads('f42.5')
	42.5
	>>> ul4on.dumps('foo')
	"S'foo'"
	>>> ul4on.loads("S'foo'")
	'foo'

:class:`datetime` and :class:`timedelta` objects are supported too::

	>>> import datetime
	>>> ul4on.dumps(datetime.datetime.now())
	'Z i2014 i11 i3 i18 i16 i45 i314157'
	>>> ul4on.loads('Z i2014 i11 i3 i18 i16 i45 i314157')
	datetime.datetime(2014, 11, 3, 18, 16, 45, 314157)
	>>> ul4on.dumps(datetime.timedelta(days=1))
	'T i1 i0 i0'
	>>> ul4on.loads('T i1 i0 i0')
	datetime.timedelta(1)

:mod:`ll.ul4on` also supports :class:`Color` objects from :mod:`ll.color`::

	>>> from ll import color
	>>> ul4on.dumps(color.red)
	'C i255 i0 i0 i255'
	>>> ul4on.loads('C i255 i0 i0 i255')
	Color(0xff, 0x00, 0x00)

Lists, dictionaries and sets are also supported::

	>>> ul4on.dumps([1, 2, 3])
	'L i1 i2 i3 ]'
	>>> ul4on.loads('L i1 i2 i3 ]')
	[1, 2, 3]
	>>> ul4on.dumps(dict(one=1, two=2))
	"D S'two' i2 S'one' i1 }"
	>>> ul4on.loads("D S'two' i2 S'one' i1 }")
	{'one': 1, 'two': 2}
	>>> ul4on.dumps({1, 2, 3})
	'Y i1 i2 i3 }'
	>>> ul4on.loads('Y i1 i2 i3 }')
	{1, 2, 3}

:mod:`ll.ul4on` can also handle recursive data structures::

	>>> r = []
	>>> r.append(r)
	>>> ul4on.dumps(r)
	'L ^0 ]'
	>>> r2 = ul4on.loads('L ^0 ]')
	>>> r2
	[[...]]
	>>> r2 is r2[0]
	True
	>>> r = {}
	>>> r['recursive'] = r
	>>> ul4on.dumps(r)
	"D S'recursive' ^0 }"
	>>> r2 = ul4on.loads("D S'recursive' ^0 }")
	>>> r2
	{'recursive': {...}}
	>>> r2['recursive'] is r2
	True

UL4ON is extensible. It supports serializing arbitrary instances by registering
the class with the UL4ON serialization machinery::

	from ll import ul4on

	@ul4on.register("com.example.person")
	class Person:
		def __init__(self, firstname=None, lastname=None):
			self.firstname = firstname
			self.lastname = lastname

		def __repr__(self):
			return f"<Person firstname={self.firstname!r} lastname={self.lastname!r}>"

		def ul4ondump(self, encoder):
			encoder.dump(self.firstname)
			encoder.dump(self.lastname)

		def ul4onload(self, decoder):
			self.firstname = decoder.load()
			self.lastname = decoder.load()

	jd = Person("John", "Doe")
	output = ul4on.dumps(jd)
	print("Dump:", output)
	jd2 = ul4on.loads(output)
	print("Loaded:", jd2)

This script outputs::

	Dump: O S'com.example.person' S'John' S'Doe' )
	Loaded: <Person firstname='John' lastname='Doe'>
"""

import datetime, collections, io, enum


__docformat__ = "reStructuredText"


_registry = {}


TYPECODE_NONE = 0
TYPECODE_BOOL = 1
TYPECODE_INT = 2
TYPECODE_FLOAT = 3
TYPECODE_STR = 4
TYPECODE_SLICE = 5
TYPECODE_COLOR = 6
TYPECODE_DATETIME = 7
TYPECODE_DATE = 8
TYPECODE_TIMEDELTA = 9
TYPECODE_MONTHDELTA = 10
TYPECODE_LIST_BEGIN = 11
TYPECODE_LIST_END = 12
TYPECODE_DICT_BEGIN = 13
TYPECODE_DICT_END = 14
TYPECODE_ODICT_BEGIN = 15
TYPECODE_ODICT_END = 16
TYPECODE_SET_BEGIN = 17
TYPECODE_SET_END = 18
TYPECODE_OBJ_BEGIN = 19
TYPECODE_OBJ_END = 20

TYPECODE_BR = 127

TYPECODE_WITH_BR = 128


def register(name):
	"""
	This decorator can be used to register the decorated class with the
	:mod:`ll.ul4on` serialization machinery.

	:obj:`name` must be a globally unique name for the class. To avoid
	name collisions Java's class naming system should be used (i.e. an
	inverted domain name like ``com.example.foo.bar``).

	:obj:`name` will be stored in the class attribute ``ul4onname``.
	"""
	def registration(cls):
		cls.ul4onname = name
		_registry[name] = cls
		return cls
	return registration


class Encoder:
	def __init__(self, stream, indent=None):
		"""
		Create an encoder for serializing objects to  :obj:`self.stream`.

		:obj:`stream` must provide a :meth:`write` method.
		"""
		self.stream = stream
		self._objects = []
		self._id2index = {}

	def _record(self, obj):
		# Record that we've written this object and in which position
		self._id2index[id(obj)] = len(self._objects)
		self._objects.append(obj)

	def _dumpint(self, value):
		bytelen = 1
		max = 128
		while bytelen < 255:
			if -max <= value < max:
				self.stream.write(bytes((bytelen,)))
				self.stream.write(value.to_bytes(bytelen, "big", signed=True))
				return
			bytelen += 1
			max *= 256
		raise OverflowError

	def dump(self, obj):
		"""
		Serialize :obj:`obj` as an UL4ON formatted stream.
		"""
		# Have we written this object already?
		if id(obj) in self._id2index:
			# Yes: Store a backreference to the object
			self.stream.write(bytes((TYPECODE_BR,)))
			self._dumpint(self._id2index[id(obj)])
		else:
			from ll import ul4c, color, misc
			# No: Write the object itself
			# We're not using backreferences if the object itself has a shorter dump
			if obj is None:
				self.stream.write(bytes((TYPECODE_NONE,)))
			elif isinstance(obj, bool):
				self.stream.write(bytes((TYPECODE_BOOL, int(obj))))
			elif isinstance(obj, int):
				self.stream.write(bytes((TYPECODE_INT,)))
				self._dumpint(obj)
			elif isinstance(obj, float):
				dump = repr(obj).encode("utf-8")
				self.stream.write(bytes((TYPECODE_FLOAT,)))
				self._dumpint(len(dump))
				self.stream.write(dump)
			elif isinstance(obj, str):
				self._record(obj)
				dump = obj.encode("utf-8")
				self.stream.write(bytes((TYPECODE_STR|TYPECODE_WITH_BR,)))
				self._dumpint(len(dump))
				self.stream.write(dump)
			elif isinstance(obj, slice):
				self._record(obj)
				self.stream.write(bytes((TYPECODE_SLICE|TYPECODE_WITH_BR,)))
				self.dump(obj.start)
				self.dump(obj.stop)
			elif isinstance(obj, color.Color):
				self._record(obj)
				self.stream.write(bytes((TYPECODE_COLOR|TYPECODE_WITH_BR, obj.r(), obj.g(), obj.b(), obj.a())))
			elif isinstance(obj, datetime.datetime):
				self._record(obj)
				self.stream.write(bytes((TYPECODE_DATETIME|TYPECODE_WITH_BR,)))
				self.stream.write(obj.year.to_bytes(2, "big", signed=True))
				self.stream.write(obj.month.to_bytes(1, "big", signed=True))
				self.stream.write(obj.day.to_bytes(1, "big", signed=True))
				self.stream.write(obj.hour.to_bytes(1, "big", signed=True))
				self.stream.write(obj.minute.to_bytes(1, "big", signed=True))
				self.stream.write(obj.second.to_bytes(1, "big", signed=True))
				self.stream.write(obj.microsecond.to_bytes(3, "big", signed=True))
			elif isinstance(obj, datetime.date):
				self._record(obj)
				self.stream.write(bytes((TYPECODE_DATE|TYPECODE_WITH_BR,)))
				self.stream.write(obj.year.to_bytes(2, "big", signed=True))
				self.stream.write(obj.month.to_bytes(1, "big", signed=True))
				self.stream.write(obj.day.to_bytes(1, "big", signed=True))
			elif isinstance(obj, datetime.timedelta):
				self._record(obj)
				self.stream.write(bytes((TYPECODE_TIMEDELTA|TYPECODE_WITH_BR,)))
				self._dumpint(obj.days)
				self._dumpint(obj.seconds)
				self._dumpint(obj.microseconds)
			elif isinstance(obj, misc.monthdelta):
				self._record(obj)
				self.stream.write(bytes((TYPECODE_MONTHDELTA|TYPECODE_WITH_BR,)))
				self._dumpint(obj.months)
			elif isinstance(obj, collections.Sequence):
				self._record(obj)
				self.stream.write(bytes((TYPECODE_LIST_BEGIN|TYPECODE_WITH_BR,)))
				for item in obj:
					self.dump(item)
				self.stream.write(bytes((TYPECODE_LIST_END,)))
			elif isinstance(obj, collections.Mapping):
				self._record(obj)
				if isinstance(obj, collections.OrderedDict):
					start = TYPECODE_ODICT_BEGIN|TYPECODE_WITH_BR
					end = TYPECODE_ODICT_END
				else:
					start = TYPECODE_DICT_BEGIN|TYPECODE_WITH_BR
					end = TYPECODE_DICT_END
				self.stream.write(bytes((start,)))
				for (key, item) in obj.items():
					self.dump(key)
					self.dump(item)
				self.stream.write(bytes((end,)))
			elif isinstance(obj, collections.Set):
				self._record(obj)
				self.stream.write(bytes((TYPECODE_SET_BEGIN|TYPECODE_WITH_BR,)))
				for item in obj:
					self.dump(item)
				self.stream.write(bytes((TYPECODE_SET_END,)))
			else:
				self._record(obj)
				self.stream.write(bytes((TYPECODE_OBJ_BEGIN|TYPECODE_WITH_BR,)))
				self.dump(obj.ul4onname)
				obj.ul4ondump(self)
				self.stream.write(bytes((TYPECODE_OBJ_END,)))


class Decoder:
	def __init__(self, stream):
		"""
		Create a decoder for deserializing objects from  :obj:`self.stream`.

		:obj:`stream` must provide a :meth:`read` method.
		"""
		self.stream = stream
		self._objects = []
		self._keycache = {} # Used for "interning" dictionary keys

	def load(self):
		"""
		Deserialize the next object in the stream and return it.
		"""
		return self._load(None)

	def _readcode(self):
		return self.stream.read(1)[0]

	def _readint(self):
		bytelen = self.stream.read(1)[0]
		dump = self.stream.read(bytelen)
		return int.from_bytes(dump, "big", signed=True)

	def _loading(self, obj):
		self._objects.append(obj)

	def _beginfakeloading(self):
		# For loading custom object or immutable objects that have attributes we have a problem:
		# We have to record the object we're loading *now*, so that it is available for backreferences.
		# However until we've read the UL4ON name of the class (for custom object) or the attributes
		# of the object (for immutable objects with attributes), we can't create the object.
		# So we push ``None`` to the backreference list for now and put the right object in this spot,
		# once we've created it (via :meth:`_endfakeloading`). This shouldn't lead to problems,
		# because during the time the backreference is wrong, only the class name is read,
		# so our object won't be referenced. For immutable objects the attributes normally
		# don't reference the object itself.
		oldpos = len(self._objects)
		self._loading(None)
		return oldpos

	def _endfakeloading(self, oldpos, value):
		# Fix backreference in object list
		self._objects[oldpos] = value

	def _load(self, typecode):
		from ll import misc
		if typecode is None:
			typecode = self._readcode()
		hasbackref = typecode > 0x7f
		typecode = typecode & 0x7f
		if typecode == TYPECODE_BR:
			position = self._readint()
			return self._objects[position]
		elif typecode == TYPECODE_NONE:
			if hasbackref:
				self._loading(None)
			return None
		elif typecode == TYPECODE_BOOL:
			value = self.stream.read(1)
			t = b"\x01"
			f = b"\x00"
			if value == t:
				value = True
			elif value == f:
				value = False
			else:
				raise ValueError(f"broken UL4ON stream at position {self.stream.tell()-1:,}: expected {f!r} or {t!r} for bool; got {value!r}")
			if hasbackref:
				self._loading(value)
			return value
		elif typecode == TYPECODE_INT:
			value = self._readint()
			if hasbackref:
				self._loading(value)
			return value
		elif typecode == TYPECODE_FLOAT:
			size = self._readint()
			dump = self.stream.read(size)
			value = float(dump.decode("utf-8"))
			if hasbackref:
				self._loading(value)
			return value
		elif typecode == TYPECODE_STR:
			size = self._readint()
			dump = self.stream.read(size)
			value = dump.decode("utf-8")
			if hasbackref:
				self._loading(value)
			return value
		elif typecode == TYPECODE_COLOR:
			from ll import color
			if hasbackref:
				oldpos = self._beginfakeloading()
			dump = self.stream.read(4)
			value = color.Color(*dump)
			if hasbackref:
				self._endfakeloading(oldpos, value)
			return value
		elif typecode == TYPECODE_DATETIME:
			if hasbackref:
				oldpos = self._beginfakeloading()
			dump = self.stream.read(10)
			year = int.from_bytes(dump[:2], "big", signed=True)
			month = dump[2]
			day = dump[3]
			hour = dump[4]
			minute = dump[5]
			second = dump[6]
			microsecond = int.from_bytes(dump[-3:], "big", signed=True)
			value = datetime.datetime(year, month, day, hour, minute, second, microsecond)
			if hasbackref:
				self._endfakeloading(oldpos, value)
			return value
		elif typecode == TYPECODE_DATE:
			if hasbackref:
				oldpos = self._beginfakeloading()
			dump = self.stream.read(4)
			year = int.from_bytes(dump[:2], "big", signed=True)
			month = dump[2]
			day = dump[3]
			value = datetime.date(year, month, day)
			if hasbackref:
				self._endfakeloading(oldpos, value)
			return value
		elif typecode == TYPECODE_SLICE:
			if hasbackref:
				oldpos = self._beginfakeloading()
			start = self._load(None)
			stop = self._load(None)
			value = slice(start, stop)
			if hasbackref:
				self._endfakeloading(oldpos, value)
			return value
		elif typecode == TYPECODE_TIMEDELTA:
			if hasbackref:
				oldpos = self._beginfakeloading()
			days = self._readint()
			seconds = self._readint()
			microseconds = self._readint()
			value = datetime.timedelta(days, seconds, microseconds)
			if hasbackref:
				self._endfakeloading(oldpos, value)
			return value
		elif typecode == TYPECODE_MONTHDELTA:
			from ll import misc
			if hasbackref:
				oldpos = self._beginfakeloading()
			months = self._readint()
			value = misc.monthdelta(months)
			if hasbackref:
				self._endfakeloading(oldpos, value)
			return value
		elif typecode == TYPECODE_LIST_BEGIN:
			value = []
			if hasbackref:
				self._loading(value)
			while True:
				typecode = self._readcode()
				if typecode == TYPECODE_LIST_END:
					return value
				else:
					item = self._load(typecode)
					value.append(item)
		elif typecode == TYPECODE_DICT_BEGIN or typecode == TYPECODE_ODICT_BEGIN:
			if typecode == TYPECODE_DICT_BEGIN:
				value = {}
				end = TYPECODE_DICT_END
			else:
				value = collections.OrderedDict()
				end = TYPECODE_ODICT_END
			if hasbackref:
				self._loading(value)
			while True:
				typecode = self._readcode()
				if typecode == end:
					return value
				else:
					key = self._load(typecode)
					if isinstance(key, str):
						if key in self._keycache:
							key = self._keycache[key]
						else:
							self._keycache[key] = key
					item = self._load(None)
					value[key] = item
		elif typecode == TYPECODE_SET_BEGIN:
			value = set()
			if hasbackref:
				self._loading(value)
			while True:
				typecode = self._readcode()
				if typecode == TYPECODE_SET_END:
					return value
				else:
					item = self._load(typecode)
					value.add(item)
		elif typecode == TYPECODE_OBJ_BEGIN:
			if hasbackref:
				oldpos = self._beginfakeloading()
			name = self._load(None)
			try:
				cls = _registry[name]
			except KeyError:
				raise TypeError(f"can't decode object of type {name}")
			value = cls()
			if hasbackref:
				self._endfakeloading(oldpos, value)
			value.ul4onload(self)
			typecode = self._readcode()
			if typecode != TYPECODE_OBJ_END:
				raise ValueError("broken UL4ON stream at position {self.stream.tell():,}: object terminator {TYPECODE_OBJ_END!r} expected, got {typecode!r}")
			return value
		else:
			raise ValueError("broken UL4ON stream at position {self.stream.tell():,}: unknown typecode {typecode!r}")


class StreamBuffer:
	# Internal helper class that wraps a file-like object and provides buffering
	def __init__(self, stream, bufsize=1024*1024):
		self.stream = stream
		self.bufsize = bufsize
		self.buffer = ""

	def read(self, size):
		havesize = len(self.buffer)
		if havesize >= size:
			result = self.buffer[:size]
			self.buffer = self.buffer[size:]
			return result
		else:
			needsize = size-havesize
			newdata = self.stream.read(max(self.bufsize, needsize))
			result = self.buffer + newdata[:needsize]
			self.buffer = newdata[needsize:]
			return result


def dumps(obj, indent=None):
	"""
	Serialize :obj:`obj` as an UL4ON formatted string.
	"""
	stream = io.BytesIO()
	encoder = Encoder(stream, indent=indent)
	encoder.dump(obj)
	return stream.getvalue()


def dump(obj, stream, indent=None):
	"""
	Serialize :obj:`obj` as an UL4ON formatted stream to :obj:`stream`.

	:obj:`stream` must provide a :meth:`write` method.
	"""
	Encoder(stream, indent=indent).dump(obj)


def loadclob(clob, bufsize=1024*1024):
	"""
	Deserialize :obj:`clob` (which must be an :mod:`cx_Oracle` ``CLOB`` variable
	containing an UL4ON formatted object) to a Python object.

	:obj:`bufsize` specifies the chunk size for reading the underlying ``CLOB``
	object.
	"""
	return Decoder(StreamBuffer(clob, bufsize)).load()


def loads(dump):
	"""
	Deserialize :obj:`dump` (which must be a ``bytes`` object containing an UL4ON
_BEGIN	formatted object) to a Python object.
	"""
	return Decoder(io.BytesIO(dump)).load()


def load(stream):
	"""
	Deserialize :obj:`stream` (which must be file-like object with a :meth:`readGIN`
	method containing an UL4ON formatted object) to a Python object.
	"""
	return Decoder(stream).load()
