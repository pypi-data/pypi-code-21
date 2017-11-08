""" Custom behavior
"""
from zope.interface import implements
from zope import schema
from zope.component import adapts
from plone.supermodel import model
from plone.z3cform.fieldsets import extensible
from eea.cache.browser.app.edit import SettingsForm
from eea.epub.interfaces import ILayer, IEPUBAware
from eea.epub.config import EEAMessageFactory as _
from eea.epub.cache.cache import updateBackRefs
from eea.epub.cache.cache import updateContext
from eea.epub.cache.cache import updateRelatedItems


class IExtraSettings(model.Schema):
    """ Extra settings
    """
    epub = schema.Bool(
        title=_(u"ePub"),
        description=_(u"Invalidate latest generated ePub file"),
        required=False,
        default=False
    )


class ExtraBehavior(object):
    """ Cache Controller
    """
    implements(IExtraSettings)
    adapts(IEPUBAware)

    def __init__(self, context):
        self.context = context

    @property
    def epub(self):
        """ ePub
        """
        return False

    @epub.setter
    def epub(self, value):
        """ Invalidate last generated ePub?
        """
        if not value:
            return

        updateContext(self.context)

        if value.get('relatedItems'):
            updateRelatedItems(self.context)

        if value.get('backRefs'):
            updateBackRefs(self.context)


class ExtraSettings(extensible.FormExtender):
    """ Cache invalidation form extender
    """
    adapts(IEPUBAware, ILayer, SettingsForm)

    def __init__(self, context, request, form):
        self.context = context
        self.request = request
        self.form = form

    def update(self):
        """ Extend form
        """
        self.add(IExtraSettings, prefix="extra")
        self.move('epub', after='varnish', prefix='extra')
