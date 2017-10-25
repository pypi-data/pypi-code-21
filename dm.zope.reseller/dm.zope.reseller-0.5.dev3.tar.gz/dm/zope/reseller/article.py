# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
"""Article management."""
from decimal import Decimal, ROUND_UP

from zope.interface import implements

from .i18n import _
from .db import Db, Table, ObjectBase
from .interfaces import IArticleSchema, IArticle


class Article(ObjectBase):
  implements(IArticleSchema)

  _SCHEMA_ = IArticleSchema


class Articles(Table):
  _TABLE_ = "reseller.article"
  _FACTORY_ = Article
  _ORDER_ = "title"



TAX = None
cent = Decimal('0.01')
def unit_price(article):
  global TAX
  if TAX is None:
    c = Db().cursor()
    c.execute("select code, percent from reseller.tax")
    TAX = dict((code, Decimal("1.00") + percent / Decimal(100)) for (code, percent) in c.fetchall())
  a = article
  price = a.catalog_price * a.price_ratio / a.package_size * TAX[a.tax_code]
  return price.quantize(cent, rounding=ROUND_UP)


def determine_article(data, error, message):
  """determine article from *data*.

  *data* is a dict with keys `provider_order_no` and `article_title`.
  *error* and *message* are functions called in case or an error
  or to issue a message. *error* has signature `field, msg, info=None`,
  *message* `msg, info=None, type="warning"`.
  """
  pon = data.get("provider_order_no")
  at = data.get("article_title")
  if pon is None and at is None:
    return error(
      "provider_order_no",
      _(u"You must specify either the Order# (prefered) or the article"),
      _(u"Item# ${item_no}", mapping=data) if "item_no" in data else None
      )
  articles = Articles()
  if pon is not None:
    a = articles.list((("provider_order_no", pon),))
    if not a: return error(
      "provider_order_no",
      _(u"Article does not exist"),
      _(u"Order# ${provider_order_no}", mapping=data)
      )
  else: # `at` is not None
    a = articles.list((("title", at),))
    if not a: return error(
      "article",
      _(u"Article does not exist"),
      at
      )
    if len(a) >= 2: return error(
      "article",
      _(u"There are several matching articles (please use Order# instead)"),
      at
      )
  a = a[0]
  if at and a.title != at:
    message(
      _(u"Article title does not correspond (ignored)"),
      _(u"Item# ${item_no}, specified title ${stitle}, catalog title ${ctitle}, order# ${order_no}",
        mapping=dict(item_no=data.get("item_no"), order_no=a.provider_order_no, stitle=at, ctitle=a.title)
        )
      )
  return a

