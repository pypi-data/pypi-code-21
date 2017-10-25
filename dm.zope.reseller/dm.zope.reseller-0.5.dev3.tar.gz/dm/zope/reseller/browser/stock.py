# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
from zope.interface import Invalid, Interface, implements
from zope.schema import Int, TextLine

from z3c.form.interfaces import WidgetActionExecutionError
from z3c.form.field import Fields

from Products.statusmessages.interfaces import IStatusMessage

from ..i18n import _
from ..stock import Stock as StockCollection

from .view import CrudMixin, CrudAddForm
from .traversal import CollectionProxy, Constant


class Stock(CollectionProxy):
  obj = Constant(StockCollection())


class StockAddForm(CrudAddForm):
  def createAndAdd(self, data):
    self._crud().add(data)
    self.ignoreRequest = True
    self.updateWidgets()
  

class IStockAddSchema(Interface):
  units = Int(title=_(u"Units"), min=0)
  article_title = TextLine(title=_(u"Article"), description=_(u"Article title"), required=False, )
  provider_order_no = TextLine(title=_(u"Order#"), required=False, )
  
  

class StockCrud(CrudMixin):
  url_pattern = None
  item_delete_check = lambda *args: False
  add_fields = Fields(IStockAddSchema)
  ADD_FORM_FACTORY = StockAddForm

  def add(self, data):
    add_msg = IStatusMessage(self.request).addStatusMessage
    def add_message(msg, info=None, type="warning"):
      msg = self.translate(msg)
      add_msg(msg, type=type)
    def handle_error(field, msg, info=None):
      raise WidgetActionExecutionError(field, Invalid(msg))
    from ..article import determine_article
    a = determine_article(data, handle_error, add_message)
    self.collection.add_item(id=a.id, units=data["units"])
    
  
