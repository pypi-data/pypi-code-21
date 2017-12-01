# -*- coding: utf-8 -*-
from zope.interface import Interface, implements, implementer
from zope.component import adapter

import zope.schema.interfaces

from z3c.form import interfaces
from z3c.form.browser.select import SelectWidget
from z3c.form.widget import FieldWidget


class ITaxonomySelect2Widget(Interface):
    """ Marker interface for the taxonomy select widget """


class TaxonomySelect2Widget(SelectWidget):
    implements(ITaxonomySelect2Widget, interfaces.ISelectWidget)

    noValueToken = ''
    size = 5


@adapter(zope.schema.interfaces.ISequence, interfaces.IFormLayer)
@implementer(interfaces.IFieldWidget)
def TaxonomySelect2FieldWidget(field, value_type, request):
    """IFieldWidget factory for SelectWidget."""
    return FieldWidget(field, TaxonomySelect2Widget(request))


@adapter(zope.schema.interfaces.ISequence, interfaces.IFormLayer)
@implementer(interfaces.IFieldWidget)
def PatchedTaxonomySelectFieldWidget(field, request):
    """IFieldWidget factory for SelectWidget."""
    return FieldWidget(field, TaxonomySelect2Widget(request))


class ISingleSelect2Widget(Interface):
    """Marker interface for single select widget"""


class SingleSelect2Widget(SelectWidget):
    implements(ISingleSelect2Widget, interfaces.ISelectWidget)
    klass = u'single-select2-widget'

    @property
    def placeholder(self):
        return self.field.placeholder

    @property
    def select2_id(self):
        return self.id.replace('-', '_')

    @property
    def items(self):
        items = super(SingleSelect2Widget, self).items
        for item in items:
            css = ''
            css_id = item.get('value').split('_-_')
            if len(css_id) > 3:
                css = 'subcategory '
                css_id = css_id[:3]
            css = '{0}{1}'.format(css, '-'.join(css_id))
            item['css'] = css
        return items


@adapter(zope.schema.interfaces.IChoice, interfaces.IFormLayer)
@implementer(interfaces.IFieldWidget)
def SingleSelect2FieldWidget(field, request):
    """IFieldWidget factory for SingleSelect2Widget"""
    return FieldWidget(field, SingleSelect2Widget(request))


class IMultiSelect2Widget(Interface):
    """Marker interface for multi select2 widget"""


class MultiSelect2Widget(SingleSelect2Widget):
    implements(IMultiSelect2Widget, interfaces.ISelectWidget)
    klass = u'multi-select2-widget'

    @property
    def items(self):
        items = super(MultiSelect2Widget, self).items
        # self.noValueToken is '--NOVALUE--'
        return [i for i in items if i['value'] != self.noValueToken]


@adapter(zope.schema.interfaces.ISequence, interfaces.IFormLayer)
@implementer(interfaces.IFieldWidget)
def MultiSelect2FieldWidget(field, request):
    """IFieldWidget factory for MultiSelect2Widget"""
    return FieldWidget(field, MultiSelect2Widget(request))
