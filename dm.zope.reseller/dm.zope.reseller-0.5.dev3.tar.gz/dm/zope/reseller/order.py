# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
from zope.interface import implements

from .i18n import _
from .db import ObjectBase, Table
from .interfaces import \
     IOrderSchema, IOrder, \
     IProviderOrderItemSchema, IProviderOrderItem, \
     IClientInOrderSchema, IClientInOrder
from .article import Articles
from .client import ClientOrderItems


class ProviderOrderItem(ObjectBase, ClientOrderItems):
  implements(IProviderOrderItem)

  _SCHEMA_ = IProviderOrderItemSchema
  _CONTEXT_FIELD_MAP_ = dict(order_id="order_id", article_id="article_id")
  
  
  def adjust(self):
    assert self.open()
    self.packages = self.optimal()[0]
    self.store()

  def open(self): return self._manager.open()
  def deletable(self):
    # we no longer support deletion
    # return self.open()
    return False

  @property
  def classification(self):
    if not self.open(): raise AttributeError # no classification
    p, perfect = self.optimal()
    sp = self.packages
    return (
      "order-perfect" if p == sp and perfect else
      "order-optimal" if p == sp else
      "order-too-high" if sp > p else
      "order-too-low"
      )

  @property
  def title(self): return self.article_title

  def optimal(self):
    """return a pair *optimal number of packages*, *perfect*."""
    u = self.client_order_units; s = self.stock_units; S = self.package_size
    if u <= s: return (0, True)
    p = (u - s) // S # candidate
    if p * S == (u - s): return (p, True)
    # `p` is too low to meet the demand - check whether `p + 1` is acceptable
    if (p + 1) * S <= self.client_order_max_units + self.max_stock_units - s:
      return ((p + 1), True)
    else: return (p, False)

##  def deactivate(self):
##    # first reopen all associated client order items
##    m = self._manager
##    for c in self.list(): m.reopen_client_order_item(c.id)
##    super(ProviderOrderItem, self).deactivate()

    

class ProviderOrderItems(Table):
  _TABLE_ = "reseller.provider_order_item"
  _FACTORY_ = ProviderOrderItem
  # Note: had to rename `units` to `total_units` (otherwise, Postgres 8.4
  #  did not perform grouping reliably)
  _SELECT_PATTERN_ = (
    "select t.*, a.title as article_title, "
    "t.catalog_price * a.price_ratio * t.packages as total_price, "
    "a.provider_order_no as article_order_no, "
    "a.package_size as package_size, "
    "count(coi.id) as no_client_order_items, "
    "coalesce(sum(coi.units), 0) as client_order_units, "
    "coalesce(sum(coalesce(coi.max_units, coi.units)), 0) as client_order_max_units, "
    "coalesce(s.units, 0) as stock_units, "
    "a.max_stock_units as max_stock_units, "
    "t.packages * a.package_size as total_units "
    "from %(table)s as t "
    "join reseller.article as a on (t.article_id = a.id) "
    "left join reseller.client_order_item as coi on (t.order_id = coi.order_id and t.article_id = coi.article_id and coi.active) "
    "left join reseller.stock as s on (t.article_id = s.article_id) "
    "where %(cond)s "
    "group by %(base_group)s, article_title, article_order_no, "
    "  package_size, stock_units, total_units, max_stock_units, total_price, a.price_ratio "
    "%(order)s"
    )
  _ORDER_ = "article_title"
  _GROUP_ = True
  _CONTEXT_FIELD_MAP_ = dict(order_id="id")
    
  

class Order(ObjectBase, ProviderOrderItems):
  """object describing a `provider_order`."""
  implements (IOrder)

  _SCHEMA_ = IOrderSchema

  _CONTEXT_FIELD_MAP = dict(order_id=id)

  def open(self): return self.order_date is None

  def add_open_client_order_items(self):
    self._ensure_open()
    c = self.cursor()
    c.execute("update reseller.client_order_item set order_id=%s where order_id is null and active",
              (self.id,)
              )

  def add_client_order_item(self, id):
    self._ensure_open()
    coi = ClientOrderItems().get_item(id)
    coi.order_id = self.id
    coi.store()
    if not self.list((("article_id", coi.article_id),)):
      # we do not yet have an order item for this article - create one
      a = Articles().get_item(coi.article_id)
      self.add_item(
        order_id=self.id,
        article_id=a.id,
        packages=0,
        catalog_price=a.catalog_price,
        )
      

  def reopen_client_order_item(self, id):
    self._ensure_open()
    c = self.cursor()
    c.execute("update reseller.client_order_item set order_id=null where order_id = %s and active and id = %s",
              (self.id, id,)
              )

  def deactivate_client_order_item(self, id):
    self._ensure_open()
    c = self.cursor()
    c.execute("update reseller.client_order_item set active=false where order_id = %s and active and id = %s",
              (self.id, id,)
              )

  def adjust_order_items(self):
    for oi in self.list(): oi.adjust()

  def _ensure_open(self): assert self.open(), _(u"Order is closed")

  def order(self):
    from datetime import datetime
    # do not change the order
##    for oi in self.list():
##      if not oi.packages and (not oi.stock_units or not oi.client_order_units):
##        oi.deactivate()
    self.order_date = datetime.now()
    self.store()


  def get_delivery(self):
    from .delivery import ProviderDeliveries
    ds = ProviderDeliveries().list((("order_id", self.id),))
    if not ds: return
    assert len(ds) == 1
    return ds[0]

  def add_delivery(self):
    assert self.get_delivery() is None, "We already have an associated delivery"
    from .delivery import ProviderDeliveries
    pds = ProviderDeliveries()
    pid = pds.add_item(order_id=self.id)
    pdi = pds.get_item(pid)
    # create "empty" provider delivery items
    for poi in self.list(): pdi.add_item(article_id=poi.article_id)
    
    
    
class Orders(Table):
  _FACTORY_ = Order
  _TABLE_ = "reseller.provider_order"
  _ORDER_ = "t.order_date desc nulls first, t.title"


class InOrderMixin(object):
  """Mixin class to bring something into the context of an order."""
  def __init__(self, order_id, *args, **kw):
    self.context_order_id = order_id
    super(InOrderMixin, self).__init__(*args, **kw)


class ClientOrderItemsInOrder(InOrderMixin, ClientOrderItems):
  """Client order items in the context of an order."""


class ClientInOrder(ObjectBase):
  implements(IClientInOrder)

  _SCHEMA_ = IClientInOrderSchema

  def _order_items(self, oid):
    coi = ClientOrderItemsInOrder(self.context_order_id)
    coi._INSTANCE_CONDITION_ = ("order_id", oid), ("client_id", self.id),
    return coi

  def assigned_order_items(self): return self._order_items(self.context_order_id)
  def unassigned_order_items(self): return self._order_items(None)


class ClientsInOrder(InOrderMixin, Table):
  _FACTORY_ = ClientInOrder
  _TABLE_ = "reseller.client"
  _SELECT_PATTERN_ = (
    "select t.id, t.title, t.description, t.active, "
    "(select count(1) from reseller.client_order_item where client_id=t.id and order_id = %%s) as assigned_order_items_no, "
    "(select count(1) from reseller.client_order_item where client_id=t.id and order_id is null) as unassigned_order_items_no "
    "from %(table)s as t "
    "where %(cond)s "
    "%(order)s"
    )
  _ORDER_ = "t.title"
  _INITIAL_PARAMS_ = "context_order_id", 
  _CONTEXT_ = "context_order_id",
