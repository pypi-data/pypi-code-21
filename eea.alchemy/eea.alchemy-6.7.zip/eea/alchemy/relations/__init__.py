""" Safe imports from eea.relations
"""
try:
    from eea.relations import component
    getForwardRelationWith = component.getForwardRelationWith
except ImportError:
    getForwardRelationWith = None

from Products.CMFCore.utils import getToolByName

def canRelate(context, item=None, uid=None):
    """ Is relation possible
    """
    if not getForwardRelationWith:
        return True

    if not item and uid:
        catalog = getToolByName(context, 'portal_catalog')
        brains = catalog(UID=uid)
        if not brains:
            return False
        try:
            item = brains[0].getObject()
        except Exception:
            return False

    return True if getForwardRelationWith(context, item) else False
