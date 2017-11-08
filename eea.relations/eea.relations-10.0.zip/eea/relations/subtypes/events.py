""" Events
"""
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides, noLongerProvides
from zope.component import queryAdapter
from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.context import SnapshotImportContext
from Products.CMFCore.utils import getToolByName
from eea.relations.subtypes.interfaces import (
    IOriginalFacetedNavigable,
    IFacetedNavigable,
)
from eea.relations.interfaces import IToolAccessor

def subtype(obj, evt):
    """ Subtype as faceted navigable
    """
    context = obj
    portal_type = getattr(context, 'portal_type', None)
    if portal_type != 'EEARelationsContentType':
        return

    # Subtype as faceted navigable
    subtyper = queryMultiAdapter((context, context.REQUEST),
        name=u'faceted_search_subtyper', default=queryMultiAdapter(
            (context, context.REQUEST), name=u'faceted_subtyper'))

    if subtyper:
        subtyper.enable()

    # Add default widgets
    widgets = queryMultiAdapter((context, context.REQUEST),
                                name=u'default_widgets.xml')
    if not widgets:
        return

    xml = widgets()
    environ = SnapshotImportContext(context, 'utf-8')
    importer = queryMultiAdapter((context, environ), IBody)
    if not importer:
        return
    importer.body = xml

def faceted_enabled(doc, evt):
    """ EVENT: faceted navigation enabled
    """
    portal_type = getattr(doc, 'portal_type', None)
    if portal_type != 'EEARelationsContentType':
        return

    noLongerProvides(doc, IOriginalFacetedNavigable)
    alsoProvides(doc, IFacetedNavigable)

def object_renamed(obj, evt):
    """ EVENT: EEARelationsContentType object renamed
    """
    # if there is no newName or oldName then it means that we don't really
    #have a renamed object event so don't do anything
    if not evt.newName or not evt.oldName:
        return
    tool = queryAdapter(obj, IToolAccessor)
    relations = tool.relations(proxy=False)
    pt_relations = getToolByName(obj, 'portal_relations')
    bad_rel = ""
    # rename relations after a EEARelationsContentType rename to avoid broken
    # relations
    for relation in relations:
        from_rel = relation['from']
        to_rel = relation['to']
        pr_from = pt_relations.get(from_rel)
        pr_to = pt_relations.get(to_rel)
        if not pr_from:
            bad_rel = from_rel
            # rename only relation that is equal to the old id
            if bad_rel == evt.oldName:
                from_field = relation.getField('from')
                from_field.set(relation, evt.newName)
        if not pr_to:
            bad_rel = to_rel
            if bad_rel == evt.oldName:
                to_field = relation.getField('to')
                to_field.set(relation, evt.newName)
