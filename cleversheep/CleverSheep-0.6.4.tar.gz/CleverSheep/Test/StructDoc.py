#!/usr/bin/env python
"""A documentation module.

This exists purely to provide a place to put some examples for
`Struct`.


Examples
========

  A simple example of a structure::

    >>> from Struct import *
    >>> class X(Struct):
    ...     a = Type.UnsignedByte
    ...     b = Type.UnsignedShort
    ...
    >>> v = X()
    >>> print(v._meta.bytes)
    array('B', [0, 0, 0, 0])
    >>>
    >>> v.a = 0x12
    >>> v.b = 0x3456
    >>> print(v._meta.bytes)
    array('B', [18, 0, 86, 52])
    >>>
    >>> print(v._meta.hex)
    ['12', '00', '56', '34']

  Notice that the C alignment rules are followed, hence the zero padding byte.
  Notice that the structure is initialised to all zero bytes.

  The default byte order is native, which for the above example is little
  endian. You can specify the byte order as in::

    >>> from Struct import *
    >>> class X(Struct):
    ...     _byteOrder = Format.BigEndian
    ...     a = Type.UnsignedByte
    ...     b = Type.UnsignedShort
    ...
    >>> v = X()
    >>> print(v._meta.bytes)
    array('B', [0, 0, 0, 0])
    >>>
    >>> v.a = 0x12
    >>> v.b = 0x3456
    >>> print(v._meta.bytes)
    array('B', [18, 0, 52, 86])
    >>>
    >>> print(v._meta.hex)
    ['12', '00', '34', '56']

  The way of defining unions should not be a surprise::

    >>> from Struct import *
    >>> class X(Union):
    ...     a = Type.UnsignedByte
    ...     b = Type.UnsignedShort
    ...
    >>> v = X()
    >>> v.b = 0x3456
    >>> print(hex(v.b))
    0x3456
    >>>
    >>> v.a = 0x12
    >>> print(hex(v.b))
    0x3412
    >>> print(v._meta.bytes)
    array('B', [18, 52])
    >>>
    >>> print(v._meta.hex)
    ['12', '34']

  `Struct` and `Union` based classed can be arbitrarily nested, with a mix of
  endianness.::

    >>> from Struct import *
    >>> class A(Union):
    ...     _byteOrder = Format.LittleEndian
    ...     a = Type.UnsignedByte
    ...     b = Type.UnsignedShort
    ...
    >>> class B(Struct):
    ...     _byteOrder = Format.BigEndian
    ...     a = Type.UnsignedByte
    ...     b = Type.UnsignedShort
    ...
    >>> class X(Struct):
    ...     a = Type.A
    ...     b = Type.B
    ...
    >>> v = X()
    >>> v.a.b = 0x3456
    >>> v.a.a = 0x12
    >>>
    >>> v.b.a = 0x78
    >>> v.b.b = 0x9abc
    >>>
    >>> print(v._meta.bytes)
    array('B', [18, 52, 120, 0, 154, 188])
    >>> print(v._meta.hex)
    ['12', '34', '78', '00', '9a', 'bc']

  Finally, through an abuse of Python syntax, you can define arrays and bit
  fields.::

    >>> from Struct import *
    >>> class A(Struct):
    ...     _byteOrder = Format.BigEndian
    ...     a = Type.UnsignedByte
    ...     b = Type.UnsignedShort
    ...
    >>> class X(Struct):
    ...     _byteOrder = Format.BigEndian
    ...     a = Type.UnsignedByte[:4]
    ...     b = Type.UnsignedByte[:4]
    ...     c = Type.UnsignedByte[3]
    ...     d = Type.A[2]
    ...
    >>> v = X()
    >>> v.a = 0x1
    >>> v.b = 0x2
    >>> v.c[0] = 0x33
    >>> v.c[1] = 0x44
    >>> v.c[-1] = 0x55
    >>>
    >>> v.d[0].a = 0x66
    >>> v.d[0].b = 0xaaaa
    >>> v.d[1].a = 0x77
    >>> v.d[1].b = 0xbbbb
    >>>
    >>> print(v._meta.hex)
    ['21', '33', '44', '55', '66', '00', 'aa', 'aa', '77', '00', 'bb', 'bb']
    >>>
    >>> X._meta.describe()
    struct X
      a                                        : UnsignedByte:4
      b                                        : UnsignedByte:4
      c                                        : UnsignedByte[3]
      d                                        : struct A[2]
          a                                    : UnsignedByte
          b                                    : UnsignedShort


User Guide
==========

  The Struct module provides the following objects:

    `Format`
        This is just provides names for the different type of
        byte ordering. These are ``Native``, ``StandardNative``,
        ``LittleEndian`` and ``BigEndian``.

    `Type`
        A single instance that provides access to the basic types and any
        structs or unions that you define.

    `Struct`
        This is the base class to use for defining classes that map to
        C structs.

    `Union`
        This is the base class to use for defining classes that map to
        C unions.


  To create a struct or union class, you simply inherit from the appropriate
  class and list the data members as class attributes. A struct looks like::

    class MyStruct(Struct):
        _byteOrder = Format.BigEndian
        a = Type.Byte               # A single byte
        b = Type.MyUnion            # A nested (already defined) union
        c = Type.UnsignedInt[20]    # An array of 20 unsigned ints.
        ...

  For a union, you simply inherit from the `Union` class instead.
  Then you simply define instances as you would normally, as in::

    v = MyStruct()

  The resulting object will appear to have a number of members, mapping to the
  names defined for the class. So ``v`` will have members called 'a', 'b', and
  'c'. The is also a special member call '_meta', which provides access to meta information
  about the struct and it underlying class. The _meta attributes are::

    bytes
        This is an array of bytes (using the standard *array*) module.
        It is this that holds the actual data. When you set or access
        an of the c-attrs, it is this that is updated or read.

        You can modify this directly, using indexing and slicing; but you must
        not bind the variable to another name or alter its size.

    s
        Returns a string representation of the bytes. This is a read-only
        property.

    hex
        Returns a list of two character strings, representing the bytes
        as hexadecimal numbers.

    size
        Returns the size of the struct or union.

    compTypeName
        This is either 'struct' or 'union'.

    typeName()
        Returns a type name for the Python class.

    describe()
        Prints a description of the struct or union.

    byteOrder
        This is the byte order code. See the standard 'struct' module for
        details.

    pad
        This defines alignment/padding; the struct is always padded up to *pad*
        bytes and aligned on a multiple of *pad* bytes.

"""



