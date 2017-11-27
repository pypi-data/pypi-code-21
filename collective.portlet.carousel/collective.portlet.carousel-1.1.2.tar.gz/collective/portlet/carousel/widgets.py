# -*- coding: utf-8 -*-
from collective.portlet.carousel.interfaces import ICarouselItemBehavior
from collective.portlet.carousel.interfaces import ICarouselPortlet
from plone.app.widgets.dx import RelatedItemsWidget
from plone.app.widgets.interfaces import IWidgetsLayer
from z3c.form.interfaces import IFieldWidget
from z3c.form.util import getSpecification
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer


@adapter(getSpecification(ICarouselItemBehavior['carousel_background_link']),  # noqa
         IWidgetsLayer)
@implementer(IFieldWidget)
def CarouselBackgroundLinkWidget(field, request):
    widget = FieldWidget(field, RelatedItemsWidget(request))
    widget.vocabulary = 'plone.app.vocabularies.Catalog'
    widget.pattern_options = widget.pattern_options.copy()
    widget.pattern_options.update({
        'selectableTypes': ['Image'],
        'maximumSelectionSize': 1
    })
    return widget


@adapter(getSpecification(ICarouselItemBehavior['carousel_link']),
         IWidgetsLayer)
@implementer(IFieldWidget)
def CarouselLinkWidget(field, request):
    widget = FieldWidget(field, RelatedItemsWidget(request))
    widget.vocabulary = 'plone.app.vocabularies.Catalog'
    widget.pattern_options = widget.pattern_options.copy()
    widget.pattern_options.update({
        'selectableTypes': None,
        'maximumSelectionSize': 1
    })
    return widget


@adapter(getSpecification(ICarouselPortlet['collection_reference']),
         IWidgetsLayer)
@implementer(IFieldWidget)
def CarouselCollectionReferenceWidget(field, request):
    widget = FieldWidget(field, RelatedItemsWidget(request))
    widget.vocabulary = 'plone.app.vocabularies.Catalog'
    widget.pattern_options = widget.pattern_options.copy()
    widget.pattern_options.update({
        'selectableTypes': ['Collection', 'Topic'],
        'maximumSelectionSize': 1
    })
    return widget


@adapter(getSpecification(ICarouselPortlet['references']),
         IWidgetsLayer)
@implementer(IFieldWidget)
def CarouselReferencesWidget(field, request):
    widget = FieldWidget(field, RelatedItemsWidget(request))
    widget.vocabulary = 'plone.app.vocabularies.Catalog'
    widget.pattern_options = widget.pattern_options.copy()
    widget.pattern_options.update({
        'selectableTypes': None,
        'maximumSelectionSize': None
    })
    return widget
