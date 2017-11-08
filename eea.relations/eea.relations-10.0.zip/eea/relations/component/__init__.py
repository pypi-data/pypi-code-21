""" Components
"""
import logging
import types
from zope.component import queryAdapter
from eea.relations.interfaces import IContentType
from eea.relations.component.interfaces import IContentTypeLookUp
from eea.relations.component.interfaces import IRelationsLookUp

logger = logging.getLogger('eea.relations.queryContentType')


def queryContentType(context):
    """ Lookup for context related content-type in portal_relations
    """
    connecter = queryAdapter(context, IContentTypeLookUp)
    if not connecter:
        if not isinstance(context, types.MethodType):
            logger.exception('No IContentTypeLookUp adapter found for '
                             '%s', context)
        return None
    return connecter()


def queryForwardRelations(context):
    """ Lookup for context possible forward relations
    """
    if not IContentType.providedBy(context):
        context = queryContentType(context)
    if not context:
        return
    connecter = queryAdapter(context, IRelationsLookUp)
    if not connecter:
        logger.exception('No IRelationsLookUp adapter found for '
                         '%s', context)
        return
    for relation in connecter.forward():
        yield relation


def queryBackwardRelations(context):
    """ Lookup for context possible backward relations
    """
    if not IContentType.providedBy(context):
        context = queryContentType(context)
    if not context:
        return
    connecter = queryAdapter(context, IRelationsLookUp)
    if not connecter:
        logger.exception('No IRelationsLookUp adapter found for '
                         '%s', context)
        return
    for relation in connecter.backward():
        yield relation


def getForwardRelationWith(context, ctype):
    """ Get forward relation with ctype

    Returns None if I can't find possible relation or
    possible relation object from portal_relations
    """
    if not IContentType.providedBy(context):
        context = queryContentType(context)
    if not context:
        return None
    new_ctype = ctype
    if not IContentType.providedBy(ctype):
        new_ctype = queryContentType(ctype)
    if not new_ctype:
        return None

    connecter = queryAdapter(context, IRelationsLookUp)
    if not connecter:
        logger.exception('No IRelationsLookUp adapter found for '
                         '%s', context)
        return None
    return connecter.forward_with(new_ctype)

def getBackwardRelationWith(context, ctype):
    """ Get backward relation with ctype

    Returns None if I can't find possible relation or
    possible relation object from portal_relations
    """
    if not IContentType.providedBy(context):
        context = queryContentType(context)
    if not context:
        return None

    if not IContentType.providedBy(ctype):
        ctype = queryContentType(ctype)
    if not ctype:
        return None

    connecter = queryAdapter(context, IRelationsLookUp)
    if not connecter:
        logger.exception('No IRelationsLookUp adapter found for '
                         '%s', context)
        return None
    return connecter.backward_with(ctype)
