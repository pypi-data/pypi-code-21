# This file is auto-generated from bandit.idl(0.7.2-79-g2db27d7) with jenerator version 0.9.4-42-g70f7539/develop
# *** DO NOT EDIT ***


import sys
import msgpack
import jubatus.common
from jubatus.common.types import *

class ArmInfo:
  TYPE = TTuple(TInt(True, 4), TFloat())

  def __init__(self, trial_count, weight):
    self.trial_count = trial_count
    self.weight = weight

  def to_msgpack(self):
    t = (self.trial_count, self.weight)
    return self.__class__.TYPE.to_msgpack(t)

  @classmethod
  def from_msgpack(cls, arg):
    val = cls.TYPE.from_msgpack(arg)
    return ArmInfo(*val)

  def __repr__(self):
    gen = jubatus.common.MessageStringGenerator()
    gen.open("arm_info")
    gen.add("trial_count", self.trial_count)
    gen.add("weight", self.weight)
    gen.close()
    return gen.to_string()

