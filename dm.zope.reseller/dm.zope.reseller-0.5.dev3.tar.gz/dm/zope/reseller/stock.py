# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
from zope.interface import implements

from .interfaces import IStockItemSchema
from .db import Table, ObjectBase

STOCK_ID = -1

class StockItem(ObjectBase):
  implements(IStockItemSchema)
  _SCHEMA_ = IStockItemSchema


class Stock(Table):
  _TABLE_ = "reseller.stock"
  _FACTORY_ = StockItem
  _SELECT_PATTERN_ = (
    "select t.article_id as id, t.units, "
    "a.title as article_title, a.provider_order_no as article_order_no, "
    "true as active "
    "from reseller.stock as t "
    "join reseller.article as a on (a.id = t.article_id) "
    "where %(cond)s "
    "%(order)s"
    )
  _ORDER_ = "article_title"

  def add_item(self, _r_=None, **kw):
    kw["_keep_readonly_"] = True
    info = self._resolve(_r_, kw)
    if not info["units"]: return
    info["article_id"] = info["id"]; del info["id"]
    __traceback_info__ = info
    c = self.cursor()
    c.execute("insert into %s(%s) values(%s) returning article_id"
              % ("reseller.stock_manual",
                 ", ".join(info.iterkeys()),
                 ", ".join("%s" for k in info.iterkeys())
                 ),
              info.values()
              )
    return c.fetchone()[0]

  def list(self, condition=(), order='', active_only=True):
    # translate `id` to `article_id`
    cl = []
    for c in condition:
      if isinstance(c, (tuple, list)) and c[0] == "id":
        c = list(c); c[0] = "article_id"; c = tuple(c)
      cl.append(c)
    return super(Stock, self).list(tuple(cl), order, False)

  def update_item(self, _id_or_r_=None, **kw):
    info = self._resolve(_id_or_r_, kw)
    old = self.get_item(info["id"])
    ounits = old["units"] if old is not None else 0
    if ounits == info["units"]: return
    self.add_item(id=info["id"], units=info["units"] - ounits)

