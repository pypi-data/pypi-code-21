# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
from zope.interface import Interface, implements
from zope.component import adapts
from zope.schema import Decimal

from z3c.form.field import Fields

from ..i18n import _
from ..interfaces import IArticleSchema
from ..article import Articles as ArticlesCollection, unit_price

from .view import CrudMixin, SearchMixin
from .traversal import CollectionProxy, Constant


class Articles(CollectionProxy):
  obj = Constant(ArticlesCollection())

class IUnitPrice(Interface):
  unit_price = Decimal(title=_(u"u-price"), description=_(u"Unit price (with tax)"), readonly=True)


class ArticlesCrud(CrudMixin):
  url_pattern = None

  @property
  def crud_fields(self):
    return super(ArticlesCrud, self).crud_fields + Fields(IUnitPrice)


class ArticlesSearch(SearchMixin):
  url_pattern = None
  search_field_names = "title", "provider_order_no"


class AdapterIUnitPrice(object):
  implements(IUnitPrice)
  adapts(IArticleSchema)
  def __init__(self, a): self.unit_price = unit_price(a)
