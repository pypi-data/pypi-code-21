# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
"""`Delivery` related views."""
from decimal import Decimal

from zope.interface import Invalid, Interface, implements
from zope.schema import Int, Bool
from zope.component import adapts, getMultiAdapter

from z3c.form.interfaces import ActionExecutionError
from z3c.form.field import Fields, FieldWidgets
from z3c.form.button import Buttons, ImageButton, handler, Handlers, \
     buttonAndHandler

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from ..i18n import _
from ..delivery import ProviderDeliveries as DeliveriesCollection, \
     ClientsInDelivery

from .interfaces import ILayer, IProxy
from .view import UdMixin, make_readonly_fields, \
     CrudEditSubForm, CrudEditForm
from .traversal import Proxy, CollectionProxy, Constant, Namespace


class Deliveries(CollectionProxy):
  obj = Constant(DeliveriesCollection())

class DeliveriesCrud(UdMixin): pass
  # likely, we want restrict deletion
  # def item_delete_check(self, item): return False


class Delivery(CollectionProxy): pass


class IOk(Interface):
  ok = Bool(title=_(u"Ok"),
            description=_(u"If set, empty input fields will be filled from the order; i.e. this field means `delivered as ordered`"),
            required=False,
            default=False,
            )

class DeliveryCrud(UdMixin):
  def item_delete_check(self, item): return False

  @property
  def crud_fields(self):
    return Fields(IOk) + super(DeliveryCrud, self).crud_fields

class IokWidgets(FieldWidgets):
  def extract(self):
    data, errors = super(IokWidgets, self).extract()
    if not errors and data.get("ok"):
      content = self.content
      if data.get("packages") is None:
        data["packages"] = content.order_packages
      if data.get("catalog_price") is None:
        data["catalog_price"] = content.order_catalog_price
    if "ok" in data: del data["ok"]
    return data, errors




##############################################################################
## Provider delivery item

class Article(CollectionProxy):
  """actually a `ProviderDeliveryItem` inside a delivery as collection of the corresponding client delivery items."""

ProviderDeliveryItem = Article

class IChangeSchema(Interface):
  change = Int(title=_(u"Change"), description=_(u"Number of units to add/remove"), required=False)

class NoneAdapter(object):
  def __init__(*args): pass
  def __getattr__(self, k): return


class ProviderDeliveryItemEditSubForm(CrudEditSubForm):
  buttons = Buttons(
    ImageButton(u"dm_zope_reseller/assign.png", "assign", condition=lambda f: f.context.state==0),
    )

  handlers = Handlers()

  @handler(buttons["assign"])
  def handle_assign(self, action):
    self.context.assign()
    # as "assign" may remove an item, we reload the whole page
    self._crud().redirect()



class ProviderDeliveryItemEditForm(CrudEditForm):
  buttons = CrudEditForm.buttons.copy()
  handlers = Handlers()

  @handler(buttons["apply"])
  def handle_apply(self, action):
    # iterate over the subforms and collect data, indexed by (client) delivery id
    errs = []; info = {}; sum = 0; action = False
    for f in self.subforms:
      f.update()
      d, e = f.extractData()
      if e: f.status = f.formErrorsMessage; errs.extend(e)
      else: 
        did = f.context.client_delivery_id
        di = info.get(did)
        if di is None: di = info[did] = dict(change=0, subforms=[])
        c = d.get("change")
        if c: di["change"] += c; sum += c; action = True
        di["subforms"].append(f)
    if errs: self.errors = errs; self.status = self.formErrorsMessage
    else:
      if sum:
        raise ActionExecutionError(
          Invalid(_(u"The sum of all changes must be 0"))
          )
      # iterate over the clients and perform the changes
      for di, i in info.iteritems():
        c = i["change"]
        if not c: continue
        try: i["subforms"][0].context.provider_delivery_item().change_client_delivery(di, c)
        except ValueError, exc:
          # This exception is handled by the framework and
          #   therefore does not lead to a transaction abort.
          #   However, we already have partially modified persistent
          #   state. Therefore, an explicit transacion abort is necessary
          from transaction import abort; abort()
          msg = _(u"Unit number for client ${client} becomes negative",
                      mapping=dict(client=f.context.client_title)
                  ) if len(exc.args) < 2 else \
                _(u"Stock capacity ${capacity} exceeded",
                  mapping=dict(capacity=exc.args[1])
                  )
          raise ActionExecutionError(Invalid(msg))
      self._crud().redirect()

  @buttonAndHandler(name="assign", title=_(u"Assign"))
  def handleAssign(self, action):
    for f in self.subforms:
      cdi = f.context
      if cdi.state == 0: cdi.assign()
    r = self.request
    r.response.redirect(r["URL2"])


class ProviderDeliveryItemUd(UdMixin):
  url_pattern = None
  batch_size = 0
  def item_edit_check(self, item): return False

  EDIT_SUBFORM_FACTORY = ProviderDeliveryItemEditSubForm
  EDIT_FORM_FACTORY = ProviderDeliveryItemEditForm
  def BOTTOM_FACTORY(ef):
    from ..stock import Stock
    s = Stock().get_item(ef.context.obj.article_id)
    s = s.units if s is not None else 0
    if s: return "<b>%s: %s</b>" % (ef._crud().translate(_("Stock")), s)

  @property
  def crud_fields(self):
    cf = super(ProviderDeliveryItemUd, self).crud_fields
    return Fields(IChangeSchema) + make_readonly_fields(cf.select("units", "order_units", "order_max_units", "client_title", "article_order_no", "state"))


class ClientsUd(UdMixin):
  url_pattern = "++client++%s"

  def item_delete_check(*unused): return False
  item_edit_check = item_delete_check

  @property
  def crud_fields(self):
    return super(ClientsUd, self).crud_fields.select(
      "client_title", "proposed", "assigned", "confirmed",
      "delivery_date", "account",
      )

  def __init__(self, *args):
    super(ClientsUd, self).__init__(*args)
    self.collection = self.context.obj.clients()

  page = ViewPageTemplateFile("controlled_page.pt")
  def receipts(self):
    self.title = "" # suppress title
    c = self.context; r = self.request; d = c.obj
    tr = self.translate
    rl = []
    for cd in self.collection.list():
      cdp = getMultiAdapter((c, cd), IProxy)
      v = ClientUd(cdp, r)
      v.headless = True
      rl.append("<h1>%s</h1>" % 
        tr(_("Delivery receipt ${delivery_date} for order ${order_title}",
             mapping=dict(
               # may want to use widgets to get a nice formatting
               delivery_date = d.title,
               order_title = d.provider_order_title,
               )
             )
           )
        + v()
                )
    return self.page(
      body="<div style='page-break-after:always'></div>".join(rl)
      )
                




class Client(CollectionProxy):
  """Actually a client delivery."""


class ClientEditSubForm(CrudEditSubForm):
  buttons = Buttons(
    ImageButton(u"dm_zope_reseller/ok.png", "confirm", condition=lambda f: f.context.state==-1),
    )

  handlers = Handlers()

  @handler(buttons["confirm"])
  def handle_confirm(self, action):
    self.context.confirm()
    # as "confirm" may remove an item, we reload the whole page
    self._crud().redirect()



class ClientEditForm(CrudEditForm):
  buttons = Buttons()
  handlers = Handlers()

  @buttonAndHandler(title=_(u"Deliver"), name="deliver",
                    condition=lambda f: f.context.obj.delivery_date is None
                    )
  def handle_deliver(self, action):
    tr = self._crud().translate
    cd = self.context.obj
    from ..delivery import ProviderDeliveries
    d = ProviderDeliveries().get_item(cd.provider_delivery_id, KeyError)
    self.context.obj.deliver(
        tr(_("Delivery ${delivery_date} for order ${order_title}",
             mapping=dict(
               # may want to use widgets to get a nice formatting
               delivery_date = d.title,
               order_title = d.provider_order_title,
               )
             )
           )
      )
    self.updateActions()

  def update(self):
    super(ClientEditForm, self).update()
    total_price = sum((f.context.total_price for f in self.subforms),
                      Decimal("0.00")
                      )
    total_order_price = sum(
      (f.context.order_price * f.context.order_units for f in self.subforms),
      Decimal("0.00")
      )
    tr = self._crud().translate
    self.bottom = """<h3 class="summary">%s</h3>
    <b>%s EUR</b> (%s) <b> - %s EUR</b> (%s) <b> = %s EUR</b> (%s)""" % (
      tr(_(u"Total price summary")),
      total_price, tr(_(u"Delivery")), 
      total_order_price, tr(_(u"Order")),
      total_price - total_order_price, tr(_(u"Difference")),
      ) + \
      """<h3 class="summary">%s</h3>""" % tr(_(u"Account"))
    cd = self.context.obj
    if cd.delivery_date is not None:
      # already delivered; account contains the cost of this delivery
      acc = "<b>%s EUR</b>" % cd.account
    else:
      # account does not yet contain the cost of this delivery
      acc = "<b>%s EUR</b> (%s) <b> - %s EUR</b> (%s) <b> = %s EUR</b> (%s)" % (
        cd.account, tr(_(u"Old account")),
        total_price, tr(_(u"Delivery")),
        cd.account - total_price, tr(_(u"New account")),
        )
    self.bottom += acc

                     

class ClientUd(UdMixin):
  url_pattern = None
  batch_size = 0

  def item_delete_check(*unused): return False
  item_edit_check = item_delete_check

  EDIT_SUBFORM_FACTORY = ClientEditSubForm
  EDIT_FORM_FACTORY = ClientEditForm

  @property
  def crud_fields(self):
    return make_readonly_fields(
      super(ClientUd, self).crud_fields.select(
        "article_title", "article_order_no", "state",
        "order_price", "order_units", "order_max_units",
        "units", "unit_price", "total_price",
        ))

  def account(self):
    from .client import AccountCrud
    from ..client import Clients
    cd = self.context.obj
    # we cheat - not sure, this will succeed
    self.context.obj = Clients().get_item(cd.client_id, KeyError)
    av = AccountCrud(self.context, self.request)
    return av()


class ClientNamespace(Namespace):
  adapts(Delivery, ILayer)

  NAME = "client"

  def OBJECT_FACTORY(self, id):
    return ClientsInDelivery(self.context.obj.id).get_item(id, KeyError)
