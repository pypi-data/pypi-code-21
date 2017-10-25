# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
from random import choice
from math import floor

from zope.interface import implements

from .i18n import _
from .db import ObjectBase, Table
from .interfaces import \
     IProviderDeliveryItemSchema, IProviderDeliveryItem, \
     IProviderDeliverySchema, IProviderDelivery
#     IClientInDeliverySchema, IClientInDelivery
from .article import Articles, unit_price
from .client import ClientDeliveryItems, \
     ClientDeliveries, ClientDelivery
from .order import Orders
from .stock import STOCK_ID


class ProviderDeliveryItem(ObjectBase, ClientDeliveryItems):
  implements(IProviderDeliveryItem)

  _SCHEMA_ = IProviderDeliveryItemSchema
  _CONTEXT_FIELD_MAP_ = dict(provider_delivery_item_id="id")
  
  
  def distribute(self):
    if self.packages is None or self.catalog_price is None: return
    delivery = self._manager
    order = Orders().get_item(delivery.order_id, KeyError)
    order_item = order.list((("article_id", self.article_id),))[0]
    # determine how many units are available
    stock_units = order_item.stock_units
    # because we redistrute everything, we in some way undo
    #  the already performed distribution to the stock by
    #  updating stock_units
    cds = ClientDeliveries()
    sd = cds.list((("provider_delivery_id", delivery.id), ("client_id", STOCK_ID)))
    if sd:
      sd = sd[0]
      for cdi in sd.list((("provider_delivery_item_id", self.id),)):
        stock_units -= cdi.units
    avail = self.packages * Articles().get_item(self.article_id).package_size \
            + stock_units
    # determine what should be assigned to clients
    # Note: For the moment, we assume that there is at most one
    #   delivery per order. This probably should change.
    # Note: For the moment, we assume at most one client order item per client
    cois = order_item.list() # the client order items for this item
    us = [coi.units for coi in cois]
    if sum(us) > avail:
      # we have fewer units available tham have been wished for
      us = dist(avail, us) # lack distributed
      avail -= sum(us)
    else:
      avail -= sum(us) # what remains
      if avail:
        # try to distribute the excess
        rus = [coi.max_units - coi.units if coi.max_units is not None else 0
               for coi in cois
               ]
        if sum(rus) > avail: rus = dist(avail, rus)
        avail -= sum(rus)
        us = [sum(i) for i in zip(us, rus)]
    # `us` now contains what the clients should get and `avail` what must
    #    go to the stock
    #  Put the information into a client indexed dict
    cd = {}
    for coi, u in zip(cois, us): cd[coi.client_id] = dict(u=u)
    assert len(cd) == len(cois) # check one order item per client 
    cd[STOCK_ID] = dict(u=avail - stock_units)
    # Extend the child dict by information about the already available
    #  client delivery items
    cdis = self.list()
    for cdi in cdis:
      cdii = cd[cds.get_item(cdi.client_delivery_id, KeyError).client_id]
      state = cdi.state
      # at most one client deliver item per state
      assert state not in cdii
      cdii[state] = cdi
    # process each client in turn
    for cid, cdii in cd.iteritems():
      # search the client delivery for this client - create one, if necessary
      cdcs = cds.list((("client_id", cid), ("provider_delivery_id", delivery.id),))
      if not cdcs:
        cdcid = cds.add_item(
          client_id=cid, provider_delivery_id=delivery.id,
          # likely, we should set the delivery date only later
          # delivery_data = today()
          )
      else:
        assert len(cdcs) == 1
        cdcid = cdcs[0].id
      # determine the number of distributed units
      #  Note: we assume that the price change has updated the
      #   articles catalog price
      #   and the prices in all existing client delivery items
      au = 0
      for state in range(3): au += cdii[state].units if state in cdii else 0
      du = cdii["u"] - au # the unit difference
      self.change_client_delivery(cdcid, du)

  def change_client_delivery(self, did, c):
    """update the client delivery by *c* units and ensure we have at most one item per state."""
    cdis = self.list((("client_delivery_id", did),))
    if c or not cdis:
      # check validity: this is special for the stock
      cd = ClientDeliveries().get_item(did)
      if cd.client_id != STOCK_ID:
        s = c
        for cdi in cdis: s += cdi.units
        if s < 0:
          raise ValueError("negative units are allowed for the stock only")
      else:
        # verify we do not take more from the stock as there is there.
        from .stock import Stock
        sa = Stock().get_item(self.article_id)
        sunits = sa.units if sa is not None else 0
        if sunits + c < 0:
          raise ValueError("stock units must not get negative", sunits)
      # update or create a state 0 item
      for cdi in cdis:
        if cdi.state == 0: cdi.units += c; cdi.store(); break
      else:
          self.add_item(
            client_delivery_id=did,
            provider_delivery_item_id=self.id,
            units=c,
            unit_price=unit_price(Articles().get_item(self.article_id)),
            state=0,
            )
    # fold items of the same state
    sd = {}
    for cdi in cdis:
      s = cdi.state
      if s in sd:
        sd[s].units += cdi.units; sd[s].store()
        cdi.deactivate()
      else: sd[s] = cdi
    self.reload()

  def deletable(self): return False

  @property
  def classification(self):
    return "delivery-missing-data" if self.packages is None or self.catalog_price is None \
           else "delivery-incomplete-distribution" if self.proposed \
           else "delivery-perfect"
           # else "delivery-incomplete-assignment" if self.assigned \

  @property
  def title(self): return self.article_title


    

class ProviderDeliveryItems(Table):
  _TABLE_ = "reseller.provider_delivery_item"
  _FACTORY_ = ProviderDeliveryItem
  # no stock support yet
  _SELECT_PATTERN_ = (
    "select t.*, a.title as article_title, "
    "a.provider_order_no as article_order_no, "
    "poi.packages as order_packages, "
    "poi.catalog_price as order_catalog_price, "
    "a.price_ratio as price_ratio, "
    "(select count(1) from reseller.client_delivery_item where units != 0 and active and provider_delivery_item_id = t.id and state = 0) as proposed, "
    "(select count(1) from reseller.client_delivery_item where units != 0 and active and provider_delivery_item_id = t.id and state = 1) as assigned "
    "from %(table)s as t "
    "join reseller.provider_delivery as pd on (t.delivery_id = pd.id) "
    "join reseller.article as a on (t.article_id = a.id) "
    "join reseller.provider_order_item as poi on (t.article_id = poi.article_id and poi.order_id = pd.order_id and poi.active)"
    "where %(cond)s "
    "%(order)s"
    )
  _ORDER_ = "article_title"
  _GROUP_ = False
    
  

class ProviderDelivery(ObjectBase, ProviderDeliveryItems):
  """object describing a `provider_delivery`."""
  implements (IProviderDelivery)

  _SCHEMA_ = IProviderDeliverySchema
  _CONTEXT_FIELD_MAP_ = dict(delivery_id="id")

  def clients(self):
    """the clients (more precisely, the client deliveries) associated with this delivery.
    """
    return ClientsInDelivery(self.id)

    
class ProviderDeliveries(Table):
  _FACTORY_ = ProviderDelivery
  _TABLE_ = "reseller.provider_delivery"
  _SELECT_PATTERN_ = (
    "select t.*, o.title as provider_order_title "
    "from %(table)s as t "
    "join reseller.provider_order as o on (t.order_id = o.id) "
    "where %(cond)s "
    "%(order)s"
    )

  _ORDER_ = "title desc"


class ClientInDelivery(ClientDelivery):
  @property
  def title(self): return self.client_title

  @property
  def classification(self):
    if self.delivery_date is not None: # or self.client_id == STOCK_ID:
      raise AttributeError() # no classification
    return "client-delivery-undelivered"

class ClientsInDelivery(ClientDeliveries):
  _FACTORY_ = ClientInDelivery
  _CONTEXT_FIELD_MAP_ = dict(provider_delivery_id="provider_delivery_id")

  def __init__(self, provider_delivery_id):
    self.provider_delivery_id = provider_delivery_id
    


def update_pdi_handler(pdi, event):
  """update handler for a provider delivery item."""
  update_price = pdi.catalog_price is not None
  redistribute = pdi.packages is not None
  ds = getattr(event, "descriptions", ())
  for d in ds:
    if d.interface is IProviderDeliveryItemSchema:
      if "catalog_price" not in d.attributes: update_price = False
      if "packages" not in d.attributes: redistribute = False
  if update_price:
    a = Articles().get_item(pdi.article_id)
    a.catalog_price = pdi.catalog_price; a.store()
    up = unit_price(a)
    for cdi in pdi.list(): cdi.unit_price = up; cdi.store()
  if redistribute: pdi.distribute()


## Auxiliaries
def dist(n, ns):
  """distribute *n* guided by *ns*.

  *n* is a positive int; *ns* is a list of positive ints. `sum(ns) >= n`.
  The result is a sequence *ms* of positive integers with
  `sum(ms) == n`, `ms[i] <= ns[i]` and `ns[j] < ns[i] => ms[j] <= ms[i]`.
  """
  s = sum(ns, 0)
  if s <= n: return ns
  r = float(n) / float(s) # ratio < 1
  ts = sorted([(nsi, i) for (i, nsi) in enumerate(ns)])
  ms = [[i, int(floor(r*nsi))] for (nsi, i) in ts]
  r = n - sum(m[1] for m in ms) # remaining < len(ms)
  eq_s = set(); v = ts[-1][0]
  def rdist(r):
    """distribute up to *r* to randomly chosen elements from `eq_s` assigning at most 1 to each - return the remaining."""
    while eq_s and r:
      i = choice(tuple(eq_s))
      ms[i][1] += 1; r -= 1; eq_s.remove(i)
    return r
  for i in range(len(ms) - 1, -1, -1):
    if ts[i][0] < v:
      r = rdist(r)
      if r == 0: break
      v = ts[i][0]
    eq_s.add(i)
  else: rdist(r) 
  return [i[1] for i in sorted(ms)]

