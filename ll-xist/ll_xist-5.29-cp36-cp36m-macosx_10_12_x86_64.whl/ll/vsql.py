# -*- coding: utf-8 -*-
# cython: language_level=3, always_allow_keywords=True

## Copyright 2016 by LivingLogic AG, Bayreuth/Germany
## Copyright 2016 by Walter Dörwald
##
## All Rights Reserved
##
## See ll/xist/__init__.py for the license


"""
"""


__docformat__ = "reStructuredText"


class AST:
	pass

class None_(AST):
	type = "const_none"

	def asjson(self):
		return {"type": "const_none"}

	@classmethod
	def fromjson(cls, json):
		return cls()


class Value(AST):
	def __init__(self, value):
		self.value = value

	def asjson(self):
		return {"type": self.type, "value": str(self.value)}

	def __repr__(self):
		return f"<{self.__class__.__module__}.{self.__class__.__qualname__} value={self.value!r} at {id(self):#x}>"


class Bool(Value):
	type = "const_bool"

	@classmethod
	def fromjson(cls, json):
		return cls(json["value"] == "True")


class Int(Value):
	type = "const_int"

	@classmethod
	def fromjson(cls, json):
		return cls(int(json["value"]))


class Number(Value):
	type = "const_number"

	@classmethod
	def fromjson(cls, json):
		return cls(float(json["value"]))


class Str(Value):
	type = "const_str"

	@classmethod
	def fromjson(cls, json):
		return cls(json["value"])


class FieldRef(Value):
	type = "field"

	@classmethod
	def fromjson(cls, json):
		return cls(json["value"])


class Unary(AST):
	def __init__(self, obj):
		self.obj = obj

	def asjson(self):
		return {"type": self.type, "children": [self.obj.asjson()]}

	@classmethod
	def fromjson(cls, json):
		return cls(*_childrenfromjson(json))


class Neg(Unary):
	type = "unop_neg"


class Not(Unary):
	type = "unop_neg"


class Binary(AST):
	def __init__(self, obj1, obj2):
		self.obj1 = obj1
		self.obj2 = obj2

	def asjson(self):
		return {"type": self.type, "children": [self.obj1.asjson(), self.obj2.asjson()]}

	@classmethod
	def fromjson(cls, json):
		return cls(*_childrenfromjson(json))


class Eq(Binary):
	type = "cmp_eq"


class NE(Binary):
	type = "cmp_ne"


class LT(Binary):
	type = "cmp_lt"


class LE(Binary):
	type = "cmp_le"


class GT(Binary):
	type = "cmp_gt"


class GE(Binary):
	type = "cmp_ge"


class Add(Binary):
	type = "binop_add"


class Sub(Binary):
	type = "binop_sub"


class Mul(Binary):
	type = "binop_mul"


class TrueDiv(Binary):
	type = "binop_truediv"


class FloorDiv(Binary):
	type = "binop_floordiv"


class Mod(Binary):
	type = "binop_mod"


def _subclasses(cls):
	yield cls
	for subcls in cls.__subclasses__():
		yield from _subclasses(subcls)

classes = {cls.type: cls for cls in _subclasses(AST) if hasattr(cls, "type")}

del _subclasses

def _childrenfromjson(json):
	return [classes[obj["type"]].fromjson(obj) for obj in json["children"]]


def fromjson(dump):
	return classes[dump["type"]].fromjson(dump)
