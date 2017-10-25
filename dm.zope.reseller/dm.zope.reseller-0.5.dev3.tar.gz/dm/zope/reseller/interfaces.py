# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
"""`reseller` major backend interfaces.

In the schema definitions below, *required* and *readonly* are primarily
hints for the presentation. The backend does not restrict the objects.
"""

from zope.interface import Interface, Attribute
from zope.schema import Int, TextLine, Text, Datetime, Date, Bool, Decimal, Choice

from dm.zope.schema.tag import Tagger

from .i18n import _
from .lib import mk_vocabulary

tag = tagger = Tagger(__name__)



class ICollection(Interface):
  """Management of a homogenous set of data records.

  The data structure is defined by `_SCHEMA_`.

  Data records in the set are identified by the field `id`.

  Usually, data records are not removed but `deactivated`.

  At the interface, data records are implemented
  by `dm.zope.schema.dataschema.SchemaDict` instances associated
  with `_SCHEMA_`. When a parameter *_r* is used below, it refers
  to such an object.
  """
  _SCHEMA_ = Attribute(u"the schema describing the data")

  def add_item(_r_=None, **kw):
    """add a new record described by *_r_*
    optionally modified by keyword parameters *kw*.
    A potentially specified `id` is ignored.

    Only fields described by `_SCHEMA_` are allowed.

    Return the `id` of the added record.
    """

  def update_item(_id_or_r_=None, **kw):
    """modify an existing data record.

    *_id_or_r_* is either the id of the record to be modified
    or a data record. In the latter case, the id of the record
    to be modified is either defined by an *id* parameter in *kw*
    of the id of the passed in record.

    A `KeyError` is raised when there is no record with the specified
    id.
    """

  def get_item(id, default=None):
    """the data record associated with *id* (or *default*)."""

  def deactivate_item(id):
    """make the data record associated with *id* invisible."""

  def list(condition=(), order=""):
    """return a list of data records satisfying *condition* ordered by *order*.

    *condition* is a sequences of tuples *field*, *value*, *op*
    (with *op* optional, defaulting to `=`).

    *order* is a blank separated sequence of field names, optionally with suffix
    `+` (default: order increasing) or `-` (order descreasing).
    
    *order* is combined with the default ordering.
    """
    

class IDataSchema(Interface):
  """General data fields shared by all object types."""
  id = tag(Int(readonly=True), key=True)
  active = tag(Bool(title=_(u"Active"), readonly=True, required=False,
                    description=_(u"For technical (database) reasons, this field has values `True` and `None`")),
               omit=True)


class IObject(IDataSchema):
  """General interface implemented by objects representing data records."""
  def deactivate(): "make invisible"
  def store(): "make persistent"
  def reload(): "reread from database"


class IOrderSchema(IDataSchema):
  """(Provider) order data schema."""
  title = TextLine(title=_(u"Target date"))
  order_date = Datetime(title=_(u"Order date"), required=False, readonly=True)


class IOrder(IObject, ICollection, IOrderSchema):
  """(Provider) order interface.

  It is also a collection of provider order items.
  """

  def add_open_client_order_items():
    """add all open client order items to this order.

    A client order item is considered open, when it is not yet
    associated with an order.
    """

  def add_client_order_item(id):
    """add client order item identified by *id*."""

  def reopen_client_order_item(id):
    """remove client order item identified by *id* (and thus make it open again)."""

  def deactivate_client_order_item(id):
    """make the client order item identified by *id* invisible."""

  def adjust_order_items():
    """adjust the `packages` field for order items, creating order items as necessary.

    See `IProviderOrderItem.adjust` for details.
    """

  def order():
    """associate `order_date`, remove items without active client order items and close the order.

    After the order has been closed, it can no longer be changed.
    This extends to client order items which are associated with this order.
    """

  def get_delivery():
    """the delivery associated with this order (or `None`).

    In the future, we may allow more than a single delivery.
    """

  def add_delivery():
    """add delivery to the order.

    For the moment, we allow only a single delivery per order.
    """


class IProviderOrderItemSchema(IDataSchema):
  order_id = Int(readonly=True)
  article_id = Int(title=_(u"Article id"), readonly=True)
  packages = Int(title=_(u"No"), description=_(u"Number of ordered packages"), min=0)
  catalog_price = Decimal(title=_(u"Price"), description=_(u"Catalog price at order time (without tax)"), required=False, readonly=True)
  # informational fields -- maybe, we move them into a different schema
  total_price = tag(Decimal(title=_(u"t-price"), description=_(u"Total price (without tax)"), required=False, readonly=True), informational=True)
  package_size = tag(Int(title=_(u"P-Size"), description=_(u"Number of units per package"), readonly=True), informational=True)
  article_title = tag(Text(title=_(u"Article"), description=_(u"Article title"), readonly=True), informational=True)
  article_order_no = tag(Text(title=_(u"Order#"), description=_(u"Article order number"), readonly=True), informational=True)
  total_units = tag(Int(title=_(u"p-units"), description=_(u"Number of units ordered with the providers"), readonly=True), informational=True)
  stock_units = tag(Int(title=_(u"Stock"), description=_(u"Unit number available on stock"), readonly=True), informational=True)
  client_order_units = tag(Int(title=_(u"c-units"), description=_(u"Number of units ordered by clients"), readonly=True), informational=True)
  client_order_max_units = tag(Int(title=_(u"M-c-units"), description=_(u"Maximal number of units ordered by clients"), readonly=True), informational=True)
  no_client_order_items = tag(Int(title=_(u"Client#"), description=_(u"Number of clients which have ordered this item"), readonly=True), informational=True)
  max_stock_units = tag(Int(title=_(u"Max-Stock"), description=_(u"Maximal number of stockable units"), readonly=True), informational=True)


class IProviderOrderItem(IObject, IProviderOrderItemSchema, ICollection):
  """A provider order item - seen as the collection of the assdociated client order items."""
  def adjust():
    """adjust `packages` to meet the demand.

    We take into account the client order items and the stock.
    We prefer buying too few than too much -- controlled by `max_stock_size`.
    """


class IArticleSchema(IDataSchema):
  title = TextLine(title=_(u"Title"))
  description = TextLine(title=_(u"Description"), required=False)
  provider_order_no = TextLine(title=_(u"Order#"), description=_(u"Order number"))
  catalog_price = Decimal(title=_(u"Price"), description=_(u"Catalog price (without tax)"))
  tax_code = Int(title=_(u"Tax"), description=_(u"Tax code"))
  unit = TextLine(title=_(u"Unit"), description=_(u"Unit description"))
  package_size = Int(title=_(u"P-Size"), description=_(u"Package size"), min=1, default=1)
  price_ratio = Int(title=_(u"Ratio"), description=_(u"Ratio between package and catalog price"))
  max_stock_units = Int(title=_(u"Stock"), description=_(u"Allowed unit number in stock"), default=0, min=0)

class IArticle(IObject, IArticleSchema):
  pass


class IClientSchema(IDataSchema):
  title = TextLine(title=_(u"Tag"), description=_(u"Short name"))
  description = TextLine(title=_(u"Name"), required=False)
  email = TextLine(title=_(u"Email"), required=False)
  phone = TextLine(title=_(u"Phone"), required=False)
  address = Text(title=_(u"Address"), required=False)
  account = tag(Decimal(title=_(u"Account"), readonly=True), informational=True)


class IClient(IObject, ICollection, IClientSchema):
  """Client interface.

  A Client is also a collection of client deliveries.
  """
  def unassigned_order_items(): 
    """the collection of order items not yet associated with an order."""

  def list_order_items_for_order(order_id): pass

  def account_items():
    """the collection of account items for the client."""


class IClientOrderItemSchema(IDataSchema):
  client_id = Int(title=_(u"Client id"), readonly=True)
  article_id = Int(title=_(u"Article id"), readonly=True)
  order_id = Int(title=_(u"Order id"), required=False)
  units = Int(title=_(u"Units"), min=0)
  max_units = Int(title=_(u"Max units"), min=0, required=False)
  note = TextLine(title=_(u"Note"), required=False)
  unit_price = Decimal(title=_(u"Price per unit"))
  order_date = Datetime(title=_(u"Order date"), readonly=True, required=False)
  # informational
  client_title = tag(TextLine(title=_(u"Client"), readonly=True), informational=True)
  article_title = tag(TextLine(title=_(u"Article"), readonly=True), informational=True)
  provider_order_no = tag(TextLine(title=_(u"Order#"), description=_(u"Order number"), readonly=True), informational=True)
  article_unit = tag(TextLine(title=_(u"Unit"), readonly=True), informational=True)
  order_title = tag(TextLine(title=_(u"Target"), readonly=True, required=False), informational=True)

class IClientOrderItem(IObject, IClientOrderItemSchema):
  """A client order item."""


class IClientDeliverySchema(IDataSchema):
  client_id = Int(title=_(u"Client id"), readonly=True)
  provider_delivery_id = Int(title=_(u"Client id"), readonly=True)
  delivery_date = Date(title=_(u"Delivery date"), readonly=True, required=False)
  # informational
  client_title = tag(TextLine(title=_(u"Client"), readonly=True), informational=True)
  proposed = tag(Int(title=_(u"prop#"), description=_(u"Number of items in state `proposed`"), readonly=True), informational=True)
  assigned = tag(Int(title=_(u"ass#"), description=_(u"Number of items in state `assigned`"), readonly=True), informational=True)
  confirmed = tag(Int(title=_(u"conf#"), description=_(u"Number of items in state `confirmed`"), readonly=True), informational=True)
  provider_order_title = tag(TextLine(title=_(u"Order"), readonly=True), informational=True)
  provider_delivery_title = tag(Date(title=_(u"Delivery"), readonly=True), informational=True)
  account = tag(Decimal(title=_(u"Account"), readonly=True), informational=True)


class IClientDelivery(IObject, ICollection, IClientDeliverySchema):
  """Client delivery.

  A client delivery is also a collection of client delivery items.
  """
  def deliver():
    """indicate that the client has got his delivery.

    After this, the delivery is closed and can no longer be modified.
    """



class IClientDeliveryItemSchema(IDataSchema):
  client_delivery_id = Int(title=_(u"Client delivery id"), readonly=True)
  provider_delivery_item_id = Int(title=_(u"Provider delivery item id"), readonly=True)
  units = Int(title=_(u"d-units"), description=_(u"Number of delivered units"))
  unit_price = Decimal(title=_(u"d-price"), description=_(u"Unit price at delivery time (with tax)"), readonly=True)
  state = Choice(title=_(u"State"), description=_(u"Delivery State"),
                 vocabulary=mk_vocabulary(
                   (0, _(u"Proposed")),
                   (1, _(u"Assigned")),
                   (2, _(u"Confirmed")),
                   ),
                 default=0,
                 )
  # informational -- may go into a separate schema
  total_price = tag(Decimal(title=_(u"t-price"), description=_(u"Total price (including tax)"), readonly=True), informational=True)
  client_title = tag(TextLine(title=_(u"Client"), description=_(u"Client title"), readonly=True), informational=True)
  article_title = tag(TextLine(title=_(u"Article"), description=_(u"Article title"), readonly=True), informational=True)
  article_order_no = tag(TextLine(title=_(u"Order#"), description=_(u"Article order number"), readonly=True), informational=True)
  order_price = tag(Decimal(title=_("o-price"), description=_(u"Unit price at order time (with tax)"), readonly=True), informational=True)
  order_units = tag(Int(title=_(u"o-units"), description=_(u"Ordered units"), readonly=True), informational=True)
  order_max_units = tag(Int(title=_(u"o-M-units"), description=_(u"Ordered maximal units"), readonly=True), informational=True)


class IClientDeliveryItem(IObject, IClientDeliveryItemSchema):
  def assign():
    """assign this item.

    In the physical world, assigning means to put the item's units into
    the client delivery basket.

    Assigning causes the assigned item to be merged with other
    assigned items.
    """

  def confirm():
    """confirm this item.

    Confirming means that is has been verified that the client
    delivery basket contains the specified unit number.
    """


class IProviderDeliverySchema(IDataSchema):
  order_id = Int(title=_(u"Order id"), readonly=True)
  title = Date(title=_(u"Delivery date"), readonly=True)
  # informational fields
  provider_order_title = tag(TextLine(title=_(u"Order"), readonly=True), informational=True)
                      

class IProviderDelivery(IProviderDeliverySchema, ICollection):
  """The provider delivery items associated with this delivery."""

  def clients():
    """the clients (their deliveries) associated with this delivery."""


class IProviderDeliveryItemSchema(IDataSchema):
  delivery_id = Int(title=_(u"The delivery id"), readonly=True)
  article_id = Int(title=_(u"Article id"), readonly=True)
  packages = Int(title=_(u"No"), description=_(u"Number of delivered packages"), min=0, required=False)
  catalog_price = Decimal(title=_(u"Price"), description=_(u"Catalog price at delivery time (without tax)"), required=False)
  # informational fields
  article_title = tag(TextLine(title=_(u"Article"), description=_(u"Article title"), readonly=True), informational=True)
  article_order_no = tag(TextLine(title=_(u"Order#"), readonly=True), informational=True)
  order_packages = tag(Int(title=_(u"Ordered"), description=_(u"Number of ordered packages"), readonly=True), informational=True)
  order_catalog_price = tag(Decimal(title=_(u"O-Price"), description=_(u"Catalog price at order time (without tax)"), readonly=True), informational=True)
  price_ratio = tag(Int(title=_(u"Ratio"), description=_(u"Ratio between package and catalog price"),readonly=True), informational=True)
  proposed = tag(Int(title=_(u"Prop-B"), description=_(u"Difference between available and proposed/assigned units"), readonly=True), informational=True)
  assigned = tag(Int(title=_(u"Ass-B"), description=_(u"Difference between proposed and assigned units"), readonly=True), informational=True)


class IProviderDeliveryItem(IObject, IProviderDeliveryItemSchema, ICollection):
  """see as a collection of the associated client delivery items."""
  def distribute():
    """create proposed client delivery items for this provided item."""


class IClientInOrderSchema(IDataSchema):
  """Client view in the context of an order."""
  # informational
  title = tag(TextLine(title=_(u"Tag"), description=_(u"Client short name"), readonly=True), informational=True)
  description = tag(TextLine(title=_(u"Name"), description=_(u"Client name"), required=False, readonly=True), informational=True)
  assigned_order_items_no = tag(Int(title=_(u"Assigned#"), description=_(u"Number of client order items assigned to this order"), readonly=True), informational=True)
  unassigned_order_items_no = tag(Int(title=_(u"Unassigned#"), description=_(u"Number of client order items not yet assigned"), readonly=True), informational=True)


class IClientInOrder(IObject, IClientInOrderSchema):
  context_order_id = Int(title=_(u"Order id"), readonly=True)

  def assigned_order_items():
    """the collection of assigned order items."""
  def unassigned_order_items():
    """the collection of unassigned order items."""


class IStockItemSchema(IDataSchema):
  units = Int(title=_(u"Units"), min=0)
  # informational fields
  article_title = tag(TextLine(title=_(u"Article"), description=_(u"Article title"), readonly=True), informational=True)
  article_order_no = tag(TextLine(title=_(u"Order#"), readonly=True), informational=True)


class IConfigItemSchema(IDataSchema):
  title = TextLine(title=_(u"Title"))
  value = Text(title=_(u"Value"), required=False)


class IAccountItemSchema(IDataSchema):
  client_id = Int(title=_(u"Client id"), readonly=True)
  account_date = Datetime(title=_(u"Account date"), readonly=True)
  note = TextLine(title=_(u"Note"), required=False)
  amount = Decimal(title=_(u"Amount"), )
