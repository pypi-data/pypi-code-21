# This file is auto-generated from clustering.idl(0.9.4-18-g4935b2b) with jenerator version 0.9.4-42-g70f7539/develop
# *** DO NOT EDIT ***


import sys
import msgpack
import jubatus.common
from jubatus.common.types import *

class WeightedDatum:
  TYPE = TTuple(TFloat(), TDatum())

  def __init__(self, weight, point):
    self.weight = weight
    self.point = point

  def to_msgpack(self):
    t = (self.weight, self.point)
    return self.__class__.TYPE.to_msgpack(t)

  @classmethod
  def from_msgpack(cls, arg):
    val = cls.TYPE.from_msgpack(arg)
    return WeightedDatum(*val)

  def __repr__(self):
    gen = jubatus.common.MessageStringGenerator()
    gen.open("weighted_datum")
    gen.add("weight", self.weight)
    gen.add("point", self.point)
    gen.close()
    return gen.to_string()

class IndexedPoint:
  TYPE = TTuple(TString(), TDatum())

  def __init__(self, id, point):
    self.id = id
    self.point = point

  def to_msgpack(self):
    t = (self.id, self.point)
    return self.__class__.TYPE.to_msgpack(t)

  @classmethod
  def from_msgpack(cls, arg):
    val = cls.TYPE.from_msgpack(arg)
    return IndexedPoint(*val)

  def __repr__(self):
    gen = jubatus.common.MessageStringGenerator()
    gen.open("indexed_point")
    gen.add("id", self.id)
    gen.add("point", self.point)
    gen.close()
    return gen.to_string()

class WeightedIndex:
  TYPE = TTuple(TFloat(), TString())

  def __init__(self, weight, id):
    self.weight = weight
    self.id = id

  def to_msgpack(self):
    t = (self.weight, self.id)
    return self.__class__.TYPE.to_msgpack(t)

  @classmethod
  def from_msgpack(cls, arg):
    val = cls.TYPE.from_msgpack(arg)
    return WeightedIndex(*val)

  def __repr__(self):
    gen = jubatus.common.MessageStringGenerator()
    gen.open("weighted_index")
    gen.add("weight", self.weight)
    gen.add("id", self.id)
    gen.close()
    return gen.to_string()

