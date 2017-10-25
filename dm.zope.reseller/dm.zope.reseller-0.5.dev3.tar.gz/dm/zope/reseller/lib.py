# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

def mk_vocabulary(*items):
  return SimpleVocabulary(tuple(SimpleTerm(i[0], title=i[1]) for i in items))


class overridable_property(object):
  """like `property` but allow for instance based overriding."""
  def __init__(self, accessor): self.__accessor = accessor

  def __get__(self, instance, owner):
    if instance is None: return self
    return self.__accessor(instance)

