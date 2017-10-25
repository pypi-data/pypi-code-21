# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
"""Configuration."""
from .db import Table, ObjectBase
from .interfaces import IConfigItemSchema


class ConfigItem(ObjectBase):
  _SCHEMA_ = IConfigItemSchema


class Config(Table):
  _TABLE_ = "reseller.config"
  _FACTORY_ = ConfigItem

  _exists_ = None
  def list(self, *args, **kw):
    if self._exists_ is None:
      c = self.cursor()
      c.execute("select count(1) from information_schema.tables where table_schema='reseller' and table_name='config'")
      self._exists_ = c.fetchone()[0]
    return super(Config, self).list(*args, **kw) if self._exists_ else ()
