# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
"""Basic views."""
from urllib import quote
from sys import maxint
from copy import copy
from decimal import Decimal

from zope.interface import implements
from zope.i18n import translate
from zope.schema import getFieldsInOrder

from z3c.form.field import Fields
from z3c.form.form import EditForm, AddForm, Form
from z3c.form.subform import EditSubForm
from z3c.form.button import ImageButton, handler, Buttons, Button, \
     buttonAndHandler, Handlers

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.z3cform.interfaces import IWrappedForm
from plone.z3cform.templates import FormTemplateFactory

from plone.batching import Batch
from plone.batching.browser import BatchView

from ..i18n import domain, _
from ..lib import overridable_property

from .interfaces import ILayer


class ViewBase(BrowserView):
  # to be defined by derived classes
  # title = the views basic title (usually a message id)
  # description = optional view explanation

  def translate(self, msgid, domain=domain, mapping=None, context=None,
               target_language=None, default=None):
    if context is None: context = self.request
    return translate(msgid, domain, mapping, context, target_language, default)




class ChildForm(object):
  """Mixin class representing a form with a parent.

  Usually the first inherited class.
  """
  def __init__(self, context, request, parent):
    self.__parent__ = parent
    super(ChildForm, self).__init__(context, request)


##############################################################################
##############################################################################
## Crud Support
##  motivated by `plone.z3cform.crud`.


def active(esf): return esf.context.active
def linkable(esf):
  return active(esf) and getattr(esf._crud(), "url_pattern", False)

def editable(esf):
  if not active(esf) or getattr(esf.fields, "mode", "input") == 'display':
    return False
  item_edit_check = getattr(esf._crud(), "item_edit_check", None)
  return True if item_edit_check is None else item_edit_check(esf.context)

def deletable(esf):
  if not active(esf): return False
  item_delete_check = getattr(esf._crud(), "item_delete_check", None)
  return True if item_delete_check is None else item_delete_check(esf.context)

def reactivatable(esf):
  # for the moment
  return not active(esf)

crud_edit_buttons = Buttons(
    Button(title=_("Apply"), name="apply",
           condition=lambda self: self.fields
           or getattr(self._crud().crud_fields, "mode", "input") != "display"
           ),
  )


class CrudEditSubForm(EditSubForm, Form):
  """The item level (sub) form."""
  template = ViewPageTemplateFile("crud-row.pt")

  buttons = Buttons(
    ImageButton(u"dm_zope_reseller/link.png", "link", condition=linkable),
    ImageButton(u"dm_zope_reseller/edit.png", "edit", condition=editable),
    ImageButton(u"dm_zope_reseller/delete.png", "delete", condition=deletable),
    ImageButton(u"dm_zope_reseller/reactivate.png", "reactivate", condition=reactivatable),
    )

  handlers = Handlers()

  successMessage = 1
  noChangesMessage = 0
  formErrorsMessage = -1

  def update(self):
    self.prefix = "crud.editsubform.%s" % self.context.id
    self.fields = self._crud().crud_fields
    super(CrudEditSubForm, self).update()


  @handler(buttons["edit"])
  def handleApply(self, action):
    super(CrudEditSubForm, self).handleApply(self, action)
    if self.status is self.successMessage:
      self.ignoreRequest = True
      self.updateWidgets()

  handler(crud_edit_buttons["apply"])(handleApply)

  @handler(buttons["link"])
  def handle_link(self, action):
    r = self.request
    r.response.redirect("%s/%s" % (
      r["URL1"],
      self._crud().url_pattern % self.context.id
      ))

  @handler(buttons["delete"])
  def handle_delete(self, action):
    self.context.deactivate()
    self._crud().redirect()

  @handler(buttons["reactivate"])
  def handle_reactivate(self, action):
    c = self.context
    c.active = True; c.store()
    self._crud().redirect()


  def _crud(self): return self.__parent__.__parent__

  @overridable_property
  def class_(self):
    return getattr(self.context, "classification", '')


class CrudEditForm(ChildForm, EditForm):
  """The item collection level edit form (a sequence of edit sub forms)."""
  template = ViewPageTemplateFile("crud-table.pt")

  @overridable_property
  def SUBFORM_FACTORY(self):
    return self._crud().EDIT_SUBFORM_FACTORY

  prefix = "crud-editform"

  buttons = crud_edit_buttons
  handlers = Handlers()

  handler(buttons["apply"])(EditForm.handleApply)

  def action(self):
    r = self.request
    return "%s?%s" % (r["URL"], r["QUERY_STRING"])

  def update(self):
    r = self.request
    self.subforms = [self.SUBFORM_FACTORY(item, r, self)
                     for item in self.batch()
                     ]
    super(CrudEditForm, self).update()
    for s in self.subforms: s.update()
    # determine the bottom
    bf = self._crud().BOTTOM_FACTORY
    if hasattr(bf, "im_func"): bf = bf.im_func
    b = bf(self)
    if b: self.bottom = b
    # compute the status, we know that for the moment we make no
    #   modifications as this level.
    status = ''
    for s in self.subforms:
      ss = s.status
      if ss == '': continue
      elif ss == -1: status = ss; break
      elif ss == 0 and status == '': status = ss
      elif ss == 1 and status != -1: status = ss
    if status != '':
      status = (self.formErrorsMessage, self.noChangesMessage, self.successMessage)[status + 1]
    self.status = status

  _batch = None
  def batch(self):
    if self._batch is None:
      crud = self._crud()
      items = crud.items()
      self._batch = Batch.fromPagenumber(
        items,
        crud.batch_size or maxint,
        int(self.request.get(self.prefix + "page", 1)),
        )
    return self._batch

  def navigation(self):
    return CrudBatchView(self.prefix, self.context, self.request)(self.batch())

  def _crud(self): return self.__parent__


class CrudBatchView(BatchView):
  def __init__(self, prefix, *args):
    self.prefix = prefix
    super(CrudBatchView, self).__init__(*args)

  def make_link(self, pagenumber):
    return "%s?%spage=%s" % (self.request["URL"], self.prefix, pagenumber)


class CrudAddForm(ChildForm, AddForm):
  """Add form."""
  implements(IWrappedForm)

  def update(self):
    self.fields = self._crud().add_fields
    super(CrudAddForm, self).update()

  def render(self): return super(AddForm, self).render()

  def createAndAdd(self, data):
    self._crud().collection.add_item(data)
    # maybe, we want to notify an ObjectCreatedEvent?
    # empty the form
    self.ignoreRequest = True
    self.updateWidgets()

  def _crud(self): return self.__parent__


class UdMixin(ViewBase):
  # Crud parameters
  batch_size = 100
  url_pattern = "++child++%s"
  EDIT_FORM_FACTORY = CrudEditForm
  EDIT_SUBFORM_FACTORY = CrudEditSubForm
  # a function applied to the edit subform
  def BOTTOM_FACTORY(ef):
    """return an HTML fragment used below the table (and above the actions)."""

  __cf = None
  @overridable_property
  def crud_fields(self):
    cf = self.__cf
    if cf is None:
      schema = self.collection._FACTORY_._SCHEMA_
      cf = self.__cf = Fields(schema).omit("active")\
           .omit(*(f for f in schema if f.endswith("id")))
      for f in cf.values():
        if f.mode is None and not f.field.readonly: break
        if f.mode is not None and f.mode != 'display': break
      else: cf.mode = 'display'  
    return cf

  @overridable_property
  def collection(self): return self.context.obj

  condition = ()
  def items(self):
    return self.collection.list(self.condition)
  # item_edit_check(item) -> bool
  # item_delete_check(item) -> bool

  index = ViewPageTemplateFile("subforms.pt")

  def __call__(self):
    self.update()
    if self.request.response.getStatus() != 200: return
    return self.render()

  def render(self):
    return self.index()

  subforms = None
  def get_subforms(self):
    subforms = self.subforms
    if subforms is None: subforms = self.subforms = []
    return subforms

  def update(self):
    subforms = self.get_subforms()
    if self.crud_fields:
      subforms.append(self.EDIT_FORM_FACTORY(self. context, self.request, self))
    for s in subforms: s.update()
    subforms.reverse()

  def redirect(self):
    r = self.request
    # must do something for batching
    r.response.redirect("%s?%s" % (r["URL"], r["QUERY_STRING"]))


class DeactivatedMixin(UdMixin):
  """Mixin class for deactivated views."""

  @overridable_property
  def crud_fields(self):
    return make_readonly_fields(super(DeactivatedMixin, self).crud_fields)

  def items(self):
    return self.collection.list((('active', None),), active_only=False)

  @overridable_property
  def title(self):
    t = self.translate
    return t(_("deactivated " + self.context.title))
    

  
class CrudMixin(UdMixin):
  """Mixin class to provide create/update/delete"""
  ADD_FORM_FACTORY = CrudAddForm

  @overridable_property
  def add_fields(self):
    return self.crud_fields.select(*
      (fn for (fn, f) in self.crud_fields.items() if not f.field.readonly)
                                   )

  def update(self):
    subforms = self.get_subforms()
    if self.add_fields:
      subforms.append(self.ADD_FORM_FACTORY(self. context, self.request, self))
    super(CrudMixin, self).update()


###############################################################################
## Search Support

class SearchForm(ChildForm, Form):
  implements(IWrappedForm)

  ignoreContext = True # maybe should become a property

  def update(self):
    self.fields = self.__parent__.search_fields
    super(SearchForm, self).update()

  @buttonAndHandler(name="search", title=_(u"Search"))
  def search(self, action):
    data, errors = self.extractData()
    if errors: self.status = self.formErrorsMessage; return
    self.__parent__.set_condition(self, data)

  @buttonAndHandler(name="reset", title=_(u"Reset"), description=_(u"Reset form"))
  def reset(self, action):
    self.ignoreRequest = True
    self.updateWidgets()


class SearchMixin(UdMixin):
  """Search view - consisting of a search form and an ud form to present the result."""
  search_field_names = "title",

  SEARCH_FORM_FACTORY = SearchForm
  search_empty = _(u"Search empty") # message

  _sf = None
  @overridable_property
  def search_fields(self):
    sf = self._sf
    if sf is None:
      sf = self._sf = Fields(*(
        # copy as we potentially modify the schema field
        copy(self.context.obj._FACTORY_._SCHEMA_[f])
        for f in self.search_field_names
        ))
      if len(sf) > 1:
        # remove `required`
        for f in sf.values(): f.field.required = False
      # maybe, we should also remove `readonly`.
    return sf

  def update(self):
    subforms = self.subforms = []
    sf = self.SEARCH_FORM_FACTORY(self.context, self.request, self)
    sf.update()
    subforms.append(sf)
    if self.condition is not None:
      sf = self.EDIT_FORM_FACTORY(self.context, self.request, self)
      sf.update()
      subforms.append(sf)

  condition = None
  def set_condition(self, form, data):
    condition = []
    for k, v in data.items():
      if v is None: continue
      if isinstance(v, unicode):
        v = v.strip()
        if not v: continue
        condition.append((k, v + u"%", "ilike"))
      else: condition.append(k, v)
    if not condition: form.status = self.search_empty; return
    self.condition = condition
    

###############################################################################
## Auxiliaries

def rooturl(ob, request):
  """workaround for bug in `z3c.form.button.ImageButtonAction` which insists that a site has been set up."""
  from .browsermenu import get_request_setup_depth
  return request["BASE%d" % get_request_setup_depth(request)]


def abspath(p):
  """return absolute path for *p* relative to this module."""
  from os.path import dirname, join
  return join(dirname(__file__), p)

# overwrite for `plone.z3cform.templates` (which forgets titles)
wrapped_form_factory = FormTemplateFactory(
  abspath("wrappedform.pt"), form=IWrappedForm, request=ILayer,
  )


def make_readonly_fields(fields):
  """return (if necessary) a copy of *fields* where no field has mode `input`."""
  nf = []
  for f in fields.values():
    if f.mode is None or f.mode == "input":
      f = copy(f); f.mode = "display"
    nf.append(f)
  r = Fields(*nf)
  r.mode = "display"
  return r


def total_price_bottom(ef):
  total_price = sum(
    (f.context.total_price for f in ef.subforms),
    Decimal("0.00")
    )
  return "<b>%s: %s EUR</b>" % (
    ef._crud().translate(_(u"Total price")),
    total_price,
    )
  
