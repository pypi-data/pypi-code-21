""" View macro utils
"""
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from eea.relations.component import getForwardRelationWith
from eea.relations.component import getBackwardRelationWith
from plone.memoize.view import memoize


class Macro(BrowserView):
    """ Categorize relations
    """

    def __init__(self, context, request):
        super(Macro, self).__init__(context, request)
        self._portal_membership = None

    @property
    def portal_membership(self):
        """ cached portal_membership as a property of Macro
        """
        if not self._portal_membership:
            self._portal_membership = getToolByName(self.context,
                                                          'portal_membership')
        return self._portal_membership

    def checkPermission(self, doc):
        """ Check document permission
        """
        mtool = self.portal_membership
        if mtool.checkPermission('View', doc):
            return doc
        return None

    def filter_relation_translations(self, relations):
        """ Filteres the translations from the relation list
            :param relations: list of relations
        """
        # this method assumes getLanguage from LinguaPlone therefore if there
        # is no such attribute on the object then we return the relations
        # unmodified
        language = getattr(self.context, 'getLanguage', None)
        if not language:
            return relations
        context_language = language()
        relations_set = set(relations)
        for relation in relations:
            if not relation:
                continue
            relation_language = relation.getLanguage()
            if context_language == relation_language:
                continue
            canonical_relation = relation.getCanonical()
            if canonical_relation in relations_set:
                if relation in relations_set:
                    relations_set.remove(relation)
        filtered_relations = list(relations_set)
        return filtered_relations

    @memoize
    def forward(self, **kwargs):
        """ Return forward relations by category
        """
        tabs = {}
        fieldname = kwargs.get('fieldname', 'relatedItems')
        field = self.context.getField(fieldname)
        if not field:
            return tabs.items()

        accessor = field.getAccessor(self.context)
        #getRelatedItems = getattr(self.context, 'getRelatedItems', None)

        contentTypes = {}
        nonForwardRelations = set()
        relations = accessor()
        filtered_relations = self.filter_relation_translations(relations)
        for relation in filtered_relations:
            if not self.checkPermission(relation) or relation.portal_type in \
                    nonForwardRelations:
                continue
            portalType = relation.portal_type

            if portalType not in contentTypes:
                forward = getForwardRelationWith(self.context, relation)
                if not forward:
                    nonForwardRelations.add(portalType)
                    continue
                name = forward.getField('forward_label').getAccessor(forward)()
                contentTypes[portalType] = name

            name = contentTypes[portalType]
            if name not in tabs:
                tabs[name] = []
            tabs[name].append(relation)
        tabs = tabs.items()
        return tabs

    @memoize
    def backward(self, **kwargs):
        """ Return backward relations by category
        """
        tabs = {}
        getBRefs = getattr(self.context, 'getBRefs', None)
        if not getBRefs:
            return tabs

        relation = kwargs.get('relation', 'relatesTo')

        relations = getBRefs(relation) or []
        contentTypes = {}
        nonBackwardRelations = set()

        filtered_relations = self.filter_relation_translations(relations)
        for relation in filtered_relations:
            # save the name and the portal type of the first relation that we
            # have permission to use.
            # this way we can check if other relations are of same portal_type
            # if they are then we don't need to check if it's a backward
            # relation and what is it's name, we can just add it to the tabs
            # for that relation name the relation item
            if not self.checkPermission(relation) or relation.portal_type in \
                    nonBackwardRelations:
                continue
            portalType = relation.portal_type
            # if the portal_type of the relation is not already in
            # contentTypes than we are dealing with a backward relation that
            # is different from the ones we had before therefore we need
            if portalType not in contentTypes:
                backward = getBackwardRelationWith(self.context, relation)
                if not backward:
                    nonBackwardRelations.add(portalType)
                    continue
                name = backward.getField('backward_label').getAccessor(
                                                                   backward)()
                contentTypes[portalType] = name

            name = contentTypes[portalType]
            if name not in tabs:
                tabs[name] = []
            tabs[name].append(relation)
        tabs = tabs.items()
        return tabs

    def forward_backward_auto(self):
        """ Return forward, backward and auto relations sorted by category
        """
        forward_relations = self.forward()
        backward_relations = self.backward()
        auto_relations = self.context.unrestrictedTraverse(
            '@@auto-relations.html').tabs
        relations = forward_relations + backward_relations + \
            list(auto_relations)

        result = {}
        for relation in relations:
            name = relation[0]
            if not result.get(name):
                result[name] = relation[1]
            else:
                result[name].extend(relation[1])
            # filter the resulting lists of duplicates
            result[name] = list(set(result[name]))

        tabs = result.items()
        tabs.sort() #this sorts based on relation label

        # sort by effective date reversed by default
        for _label, relations in tabs:
            relations.sort(cmp=lambda x, y: cmp(x.effective(),
                                               y.effective()),
                           reverse=True)
        return tabs
