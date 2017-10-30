# This file is auto-generated from weight.idl(0.9.0-24-gda61383) with jenerator version 0.9.4-42-g70f7539/develop
# *** DO NOT EDIT ***


import sys
import msgpack
import jubatus.common
from jubatus.common.types import *

class Feature:
  TYPE = TTuple(TString(), TFloat())

  def __init__(self, key, value):
    self.key = key
    self.value = value

  def to_msgpack(self):
    t = (self.key, self.value)
    return self.__class__.TYPE.to_msgpack(t)

  @classmethod
  def from_msgpack(cls, arg):
    val = cls.TYPE.from_msgpack(arg)
    return Feature(*val)

  def __repr__(self):
    gen = jubatus.common.MessageStringGenerator()
    gen.open("feature")
    gen.add("key", self.key)
    gen.add("value", self.value)
    gen.close()
    return gen.to_string()

