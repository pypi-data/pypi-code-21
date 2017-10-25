# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
"""`zope.zrdb` patching for `IDatabaseExecuteExceptionEvent`."""
from logging import getLogger
from decorator import decorator

from zope.event import notify
from zope.interface import Attribute, implements
from zope.component.interfaces import IObjectEvent

logger = getLogger(__name__)

class IDatabaseExecuteEvent(IObjectEvent):
  """Event associated with a database execute."""
  # object -- the associated cursor
  method = Attribute("Name of the called method (`execute` or `executemany`)")
  operation = Attribute("before a potential `preparation`")
  parameters = Attribute("before a potential `preparation`")

class IDatabaseExecuteSetupEvent(IDatabaseExecuteEvent):
  """notified before the `execute`.

  The event's *operation* and *parameter* are passed on to the method
  (not the original values). This gives subscribers a means to
  transform these values.
  """

class IDatabaseExecuteExceptionEvent(IDatabaseExecuteEvent):
  """notified when `execute` raised an exception."""
  exc = Attribute("the raised exception")

class IDatabaseExecuteFinishEvent(IDatabaseExecuteEvent):
  result = Attribute("the execute's result (usually `None`)")


class DatabaseExecuteEvent(object):
  implements(IDatabaseExecuteEvent)
  def __init__(self, object, method, operation, parameters):
    self.object = object; self.method = method
    self.operation = operation; self.parameters = parameters

class DatabaseExecuteSetupEvent(DatabaseExecuteEvent): pass

class DatabaseExecuteExceptionEvent(DatabaseExecuteEvent):
  def __init__(self, object, method, operation, parameters, exc):
    super(DatabaseExecuteExceptionEvent, self).__init__(object, method, operation, parameters)
    self.exc = exc

class DatabaseExecuteFinishEvent(DatabaseExecuteEvent):
  def __init__(self, object, method, operation, parameters, result):
    super(DatabaseExecuteFinishEvent, self).__init__(object, method, operation, parameters)
    self.result = result  


@decorator
def wrap(f, self, operation, parameters=None):
  def mk_event(cls, *args):
    return cls(self.cursor, f.__name__, operation, parameters, *args)
  se = mk_event(DatabaseExecuteSetupEvent)
  notify(se)
  try: r = f(self, se.operation, se.parameters)
  except Exception, e:
    notify(mk_event(DatabaseExecuteExceptionEvent, e))
    raise
  else:
    notify(mk_event(DatabaseExecuteFinishEvent, r))
    return r


logger.info("wrapping `execute` and `executemany` of `zope.zrdb.ZopeCursor` for `IDatabaseExecuteEvent` support")
from zope.rdb import ZopeCursor 

ZopeCursor.execute = wrap(ZopeCursor.execute.im_func)
ZopeCursor.executemany = wrap(ZopeCursor.executemany.im_func)
