""" Events
"""
import logging
from zope.component import queryAdapter
from zope.component.hooks import getSite
from Products.statusmessages.interfaces import IStatusMessage
from eea.alchemy.controlpanel.interfaces import IAlchemySettings
from eea.alchemy.interfaces import IDiscoverAdapter
from eea.alchemy.config import EEAMessageFactory as _
logger = logging.getLogger('eea.alchemy')

def _auto_relations(obj):
    """ Auto update relations from internal links
    """
    site = getSite()
    settings = queryAdapter(site, IAlchemySettings)
    if not settings:
        return

    if not settings.autoRelations:
        return

    fields = settings.autoRelationsFields

    lookup = queryAdapter(obj, IDiscoverAdapter, name=u'relatedItems')
    if not lookup:
        return

    lookup.metadata = fields
    lookup.tags = u'Update'

    return [tag for tag in lookup.tags]


def auto_relations(obj, event):
    """ Auto update relations from internal links
    """
    msg = u""
    tags = []
    level = u'info'
    try:
        tags = _auto_relations(obj)
    except Exception, err:
        logger.exception(err)
        msg = _(
            u"An error occured while trying to auto-relate content: %s" % err)
        level = u'error'
    else:
        length = len(tags) if tags else 0
        if length == 1:
            text = 'one relation since it is linked in content'
        else:
            text = '%s relations since they are linked in content' % length
        msg = _(u"Automatically detected and added %s. "
                "If you do not wish some relations to "
                "some content, please remove the internal link to it and than "
                "manually remove the relation" % text)

    request = getattr(obj, 'REQUEST', None)
    if not request:
        return msg

    if not tags:
        return msg

    IStatusMessage(request).add(msg, level)
