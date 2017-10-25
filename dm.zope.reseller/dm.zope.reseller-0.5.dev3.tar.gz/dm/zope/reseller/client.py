# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
from datetime import date

from zope.interface import implements

from .db import Table, ObjectBase
from .interfaces import \
     IClientSchema, IClient, \
     IClientOrderItemSchema, IClientOrderItem, \
     IClientDeliverySchema, IClientDelivery, \
     IClientDeliveryItemSchema, IClientDeliveryItem, \
     IAccountItemSchema


class ClientDeliveryItem(ObjectBase):
  implements(IClientDeliveryItem)

  _SCHEMA_ = IClientDeliveryItemSchema

  def assign(self): self.state = 1; self._fixup()
  def confirm(self): self.state = 2; self._fixup()

  def provider_delivery_item(self):
    from .delivery import ProviderDeliveryItems
    return ProviderDeliveryItems().get_item(self.provider_delivery_item_id, KeyError)

  def _fixup(self):
    self.store()
    # ensure we have only one item per state
    self.provider_delivery_item().change_client_delivery(
      self.client_delivery_id, 0
      )

  @property
  def classification(self):
    return (
      "client-delivery-item-proposed",
      "client-delivery-item-assigned",
      "client-delivery-item-confirmed",
      )[self.state]


class ClientDeliveryItems(Table):
  _TABLE_ = "reseller.client_delivery_item"
  _FACTORY_ = ClientDeliveryItem
  _SELECT_PATTERN_ = (
    "select t.*, c.title as client_title, a.title as article_title, "
    "  t.units * t.unit_price as total_price, "
    "  a.provider_order_no as article_order_no, "
    "  coalesce(max(coi.unit_price), 0.00) as order_price, "
    "  coalesce(sum(coi.units), 0) as order_units, "
    "  coalesce(sum(coalesce(coi.max_units, coi.units)), 0) as order_max_units "
    "from %(table)s as t "
    "join reseller.client_delivery as d on (t.client_delivery_id = d.id) "
    "join reseller.client as c on (d.client_id = c.id) "
    "join reseller.provider_delivery_item as pdi on (t.provider_delivery_item_id = pdi.id) "
    "join reseller.provider_delivery as pd on (pdi.delivery_id = pd.id) "
    "join reseller.article as a on (pdi.article_id = a.id) "
    "left join reseller.client_order_item as coi on (coi.client_id = d.client_id and coi.article_id = pdi.article_id and coi.order_id = pd.order_id and coi.active) "
    "where %(cond)s "
    "group by %(base_group)s, article_title, article_order_no, client_title "
    "%(order)s"
    )
  _ORDER_ = "article_title, client_title"
  _GROUP_ = True


class ClientDelivery(ObjectBase, ClientDeliveryItems):
  implements(IClientDelivery)

  # `ObjectBase`
  _SCHEMA_ = IClientDeliverySchema
  _CONTEXT_FIELD_MAP_ = dict(client_delivery_id="id")

  def deliver(self, note=None):
    self.delivery_date = date.today()
    self.store()
    # update account
    cdis = self.list()
    if cdis:
      ac = AccountItems()
      ac.add_item(client_id = self.client_id,
                  amount = -sum(i.total_price for i in cdis),
                  note = note,
                  )
      self.reload()

  @property
  def classification(self):
    if self.delivery_date is not None: return ''
    return "client-delivery-incomplete-assignment" if self.proposed \
           else "client-delivery-incomplete-confirmation" if self.assigned \
           else "client-delivery-perfect"

  @property
  def title(self): return self.provider_delivery_title


class ClientDeliveries(Table):
  _TABLE_ = "reseller.client_delivery"
  _FACTORY_ = ClientDelivery
  _SELECT_PATTERN_ = (
    "select t.*, "
    "c.title as client_title, "
    "(select count(1) from reseller.client_delivery_item as cdi where cdi.client_delivery_id = t.id and active and cdi.state = 0) as proposed, "
    "(select count(1) from reseller.client_delivery_item as cdi where cdi.client_delivery_id = t.id and active and cdi.state = 1) as assigned, "
    "(select count(1) from reseller.client_delivery_item as cdi where cdi.client_delivery_id = t.id and active and cdi.state = 2) as confirmed, "
    "po.title as provider_order_title, pd.title as provider_delivery_title, "
    "coalesce((select sum(amount) from reseller.account_item as ai where ai.client_id = c.id) , 0::decimal(10,2)) as account "
    "from %(table)s as t "
    "join reseller.client as c on (t.client_id = c.id) "
    "join reseller.provider_delivery as pd on (t.provider_delivery_id = pd.id) "
    "join reseller.provider_order as po on (pd.order_id = po.id) "
    "where %(cond)s %(order)s"
    )
  _ORDER_ = "provider_delivery_title desc, client_title"


class AccountItem(ObjectBase):
  _SCHEMA_ = IAccountItemSchema

class AccountItems(Table):
  _FACTORY_ = AccountItem
  _TABLE_ = "reseller.account_item"
  _ORDER_ = "account_date desc"


class Client(ObjectBase, ClientDeliveries):
  implements(IClient)

  # `ObjectBase`
  _SCHEMA_ = IClientSchema
  _CONTEXT_FIELD_MAP_ = dict(client_id="id")


  def unassigned_order_items(self):
    m = ClientOrderItems()
    m._INSTANCE_CONDITION_ = ("client_id", self.id), ("order_id", None),
    return m

  def list_order_items_for_order(self, order_id):
    m = ClientOrderItems()
    return m.list((("id", self.id), ("order_id", order_id),))

  def account_items(self):
    m = AccountItems()
    m._INSTANCE_CONDITION_ = ("client_id", self.id),
    return m


class Clients(Table):
  """Client management."""
  _FACTORY_ = Client
  _TABLE_ = "reseller.client"
  _SELECT_PATTERN_ = (
    "select t.*, "
    "coalesce((select sum(amount) from reseller.account_item as ai where ai.client_id = t.id) , 0::decimal(10,2)) as account "
    "from %(table)s as t "
    "where %(cond)s %(order)s"
    )
  _ORDER_ = "title"


class ClientOrderItem(ObjectBase):
  implements(IClientOrderItem)

  _SCHEMA_ = IClientOrderItemSchema


class ClientOrderItems(Table):
  """client order item management."""
  _FACTORY_ = ClientOrderItem
  _TABLE_ = "reseller.client_order_item"

  _SELECT_PATTERN_ = (
    "select t.*, c.title as client_title, "
    "a.title as article_title, a.unit as article_unit, "
    "a.provider_order_no as provider_order_no, "
    "o.title as order_title "
    "from %(table)s as t "
    "join reseller.client as c on (t.client_id = c.id) "
    "join reseller.article as a on (t.article_id = a.id) "
    "left join reseller.provider_order as o on (t.order_id = o.id) "
    "where %(cond)s %(order)s"
    )
  _ORDER_ = "article_title"
