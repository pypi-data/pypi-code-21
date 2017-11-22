from interfaces import ICarouselPortlet

from plone.app.portlets.portlets import base

from zope.interface import implements


class CarouselPortletAssignment(base.Assignment):
    implements(ICarouselPortlet)

    title = ''
    collection_reference = None
    references = []
    limit = 5
    automatic_rotation = True
    omit_border = False
    timeout = 8
    carousel_extlink = ''
