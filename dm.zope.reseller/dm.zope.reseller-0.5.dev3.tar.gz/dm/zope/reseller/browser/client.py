# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
from plone.z3cform.crud.crud import NullForm

from ..i18n import _
from ..client import Clients as ClientsCollection

from .view import CrudMixin, UdMixin, SearchMixin, make_readonly_fields
from .traversal import CollectionProxy, Constant


class Clients(CollectionProxy):
  obj = Constant(ClientsCollection())


class ClientsCrud(CrudMixin):
  css_class = "client"


class ClientsSearch(SearchMixin):
  css_class = "client"


class Client(CollectionProxy): pass


class ClientCrud(UdMixin):
  url_pattern = "++child++%s"


from .delivery import Client as ClientDelivery
class Delivery(ClientDelivery): pass

from .delivery import ClientUd as ClientDeliveryUd
class DeliveryCrud(ClientDeliveryUd):
  url_pattern = None
  def item_edit_check(*unused): return False
  item_delete_check = item_edit_check

  @property
  def crud_fields(self):
    return make_readonly_fields(super(DeliveryCrud, self).crud_fields.omit("state"))


class AccountCrud(CrudMixin):
  url_pattern = None
  item_delete_check = lambda *unused: False
  batch_size = 10

  @property
  def collection(self):
    return self.context.obj.account_items()

  def BOTTOM_FACTORY(ef):
    ud = ef._crud()
    c =  ud.context.obj
    c.reload() # force update
    return "<b>%s: %s</b>" % (ud.translate(_("Account")), c.account)
