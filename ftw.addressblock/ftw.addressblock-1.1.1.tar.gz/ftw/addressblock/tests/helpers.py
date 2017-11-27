from Products.CMFCore.utils import getToolByName


def allow_content_type(portal, contenttype, within):
    """
    This helper function can be used to allow a type within another type.
    """
    portal_types = getToolByName(portal, 'portal_types')
    fti = portal_types.get(within)
    fti.allowed_content_types += (contenttype,)
