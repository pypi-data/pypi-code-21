# copyright 2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""Adapters to export content to RDF"""

from cubicweb.predicates import is_instance

from cubes.skos import rdfio, entities as skos

from .. import permanent_url


def _prov_mapping(reg, etype):
    """Register RDF mapping for PROV-O entity types related to some entity type (prov:Agent).
    """
    reg.register_prefix('prov', 'http://www.w3.org/ns/prov#')
    reg.register_etype_equivalence('Activity', 'prov:Activity')
    reg.register_attribute_equivalence('Activity', 'type', 'prov:type')
    reg.register_attribute_equivalence('Activity', 'description', 'prov:label')
    reg.register_attribute_equivalence('Activity', 'start', 'prov:startedAtTime')
    reg.register_attribute_equivalence('Activity', 'end', 'prov:endedAtTime')
    reg.register_relation_equivalence('Activity', 'associated_with', 'CWUser',
                                      'prov:wasAssociatedWith')
    reg.register_relation_equivalence('Activity', 'generated', etype, 'prov:generated')
    reg.register_relation_equivalence('Activity', 'used', etype, 'prov:used')


def _base_rdf_mapping(reg, etype, kind):
    reg.register_prefix('foaf', 'http://xmlns.com/foaf/0.1/')
    reg.register_prefix('org', 'http://www.w3.org/ns/org#')
    reg.register_prefix('dc', 'http://purl.org/dc/elements/1.1/')
    reg.register_etype_equivalence(etype, kind)
    reg.register_attribute_equivalence(
        etype, lambda entity: u'ark:/' + entity.ark, 'dc:identifier')


def _complete_agent_rdf_mapping(reg, etype):
    reg.register_prefix('dct', 'http://purl.org/dc/terms/')
    reg.register_prefix('schema_org', 'http://schema.org/')
    reg.register_prefix('vcard', 'http://www.w3.org/2006/vcard/ns#')
    reg.register_attribute_equivalence(etype, 'creation_date', 'dct:created')
    reg.register_attribute_equivalence(etype, 'modification_date', 'dct:modified')


def _complete_authority_record_rdf_mapping(reg):
    _complete_agent_rdf_mapping(reg, 'AuthorityRecord')
    _prov_mapping(reg, 'AuthorityRecord')
    reg.register_attribute_equivalence('AuthorityRecord', lambda x: x.dc_title(), 'foaf:name')
    reg.register_attribute_equivalence('AuthorityRecord', 'start_date', 'schema_org:startDate')
    reg.register_attribute_equivalence('AuthorityRecord', 'end_date', 'schema_org:endDate')
    reg.register_etype_equivalence('PostalAddress', 'vcard:Location')
    reg.register_attribute_equivalence('PostalAddress', 'street', 'vcard:street-address')
    reg.register_attribute_equivalence('PostalAddress', 'postalcode', 'vcard:postal-code')
    reg.register_attribute_equivalence('PostalAddress', 'city', 'vcard:locality')
    reg.register_attribute_equivalence('PostalAddress', 'country', 'vcard:country-name')
    reg.register_attribute_equivalence('PostalAddress', 'state', 'vcard:region')


class AgentRDFListAdapter(skos.AbstractRDFAdapter):
    __regid__ = 'RDFList'
    __select__ = is_instance('Agent')

    def register_rdf_mapping(self, reg):
        _base_rdf_mapping(reg, self.entity.cw_etype, 'foaf:Person')
        reg.register_attribute_equivalence(
            self.entity.cw_etype, 'name', 'foaf:name')


class OrgRDFListAdapter(skos.AbstractRDFAdapter):
    __regid__ = 'RDFList'
    __select__ = is_instance('Organization', 'OrganizationUnit')

    def register_rdf_mapping(self, reg):
        etype = self.entity.cw_etype
        _base_rdf_mapping(reg, etype, 'org:{0}'.format(etype))
        reg.register_attribute_equivalence(etype, 'name', 'dc:title')


class AgentRDFPrimaryAdapter(AgentRDFListAdapter):
    __regid__ = 'RDFPrimary'
    __select__ = is_instance('Agent')

    def register_rdf_mapping(self, reg):
        super(AgentRDFPrimaryAdapter, self).register_rdf_mapping(reg)
        _complete_agent_rdf_mapping(reg, self.entity.cw_etype)


class OrganizationUnitRDFPrimaryAdapter(OrgRDFListAdapter):
    __regid__ = 'RDFPrimary'
    __select__ = is_instance('OrganizationUnit')

    def register_rdf_mapping(self, reg):
        super(OrganizationUnitRDFPrimaryAdapter, self).register_rdf_mapping(reg)
        _complete_agent_rdf_mapping(reg, self.entity.cw_etype)
        reg.register_relation_equivalence(
            'OrganizationUnit', 'contact_point', 'Agent',
            'schema_org:contactPoint')
        reg.register_relation_equivalence(
            'OrganizationUnit', 'authority', 'Organization',
            'org:unitOf')

    def fill(self, graph):
        super(OrganizationUnitRDFPrimaryAdapter, self).fill(graph)
        reg = self.registry
        # Export archival roles for the agent
        for archival_role in self.entity.archival_role:
            graph.add(graph.uri(permanent_url(self.entity)),
                      graph.uri(reg.normalize_uri('vcard:role')),
                      archival_role.name)
        # Export contact agent
        if self.entity.contact_point:
            contact_agent = self.entity.contact_point[0]
            contact_agent.cw_adapt_to('RDFPrimary').fill(graph)
        # Export related organization
        if self.entity.authority:
            org = self.entity.authority[0]
            org.cw_adapt_to('RDFPrimary').fill(graph)


class OrganizationRDFPrimaryAdapter(OrgRDFListAdapter):
    __regid__ = 'RDFPrimary'
    __select__ = is_instance('Organization')

    def register_rdf_mapping(self, reg):
        super(OrganizationRDFPrimaryAdapter, self).register_rdf_mapping(reg)
        _complete_agent_rdf_mapping(reg, self.entity.cw_etype)
        reg.register_prefix('saem', 'http://www.logilab.org/saem/0#')
        reg.register_relation_equivalence(
            'Organization', 'archival_unit', 'OrganizationUnit',
            'saem:archivalUnit')
        reg.register_relation_equivalence(
            'Organization', 'archival_authority', 'Organization',
            'saem:archivalAuthority')


class AuthorityRecordRDFPrimaryAdapter(skos.AbstractRDFAdapter):
    __regid__ = 'RDFPrimary'
    __select__ = is_instance('AuthorityRecord')

    hierarchical_role = 'http://www.logilab.org/saem/hierarchical_role'
    association_role = 'http://www.logilab.org/saem/association_role'

    def register_rdf_mapping(self, reg):
        """RDF mapping for AuthorityRecord entity type."""
        reg.register_prefix('org', 'http://www.w3.org/ns/org#')
        reg.register_prefix('foaf', 'http://xmlns.com/foaf/0.1/')
        kind = {'person': 'foaf:Person',
                'authority': 'org:OrganizationUnit',
                'family': 'foaf:Group'}.get(self.entity.kind, 'foaf:Person')
        _base_rdf_mapping(reg, 'AuthorityRecord', kind)
        _complete_authority_record_rdf_mapping(reg)

    def accept(self, entity):
        """Return True if the entity should be recursivly added to the graph."""
        return entity.cw_etype == 'Activity'

    def fill(self, graph):
        super(AuthorityRecordRDFPrimaryAdapter, self).fill(graph)
        reg = self.registry
        generator = rdfio.RDFGraphGenerator(graph)
        # Export addresses
        for place in self.entity.reverse_place_agent:
            for address in place.place_address:
                graph.add(graph.uri(permanent_url(self.entity)),
                          graph.uri(reg.normalize_uri('vcard:hasAddress')),
                          graph.uri(permanent_url(address)))
                if place.role:
                    graph.add(graph.uri(permanent_url(address)),
                              graph.uri(reg.normalize_uri('vcard:role')),
                              place.role)
                generator.add_entity(address, reg)
        # rtype name: (subj property, obj property)
        rtype_to_properties = {
            'reverse_chronological_successor': ('dct:replaces', 'dct:isReplacedBy'),
            'reverse_chronological_predecessor': ('dct:isReplacedBy', 'dct:replaces'),
            'reverse_hierarchical_parent': ('org:organization', 'org:member'),
            'reverse_hierarchical_child': ('org:member', 'org:organization'),
        }
        # Export chronological relations
        relations_generator = _iter_on_relations(
            self.entity,
            [('reverse_chronological_successor', 'chronological_predecessor'),
             ('reverse_chronological_predecessor', 'chronological_successor')])
        for rtype_name, relation, related_record in relations_generator:
            to_predicate, from_predicate = rtype_to_properties[rtype_name]
            graph.add(graph.uri(permanent_url(related_record)),
                      graph.uri(reg.normalize_uri(from_predicate)),
                      graph.uri(permanent_url(self.entity)))
            graph.add(graph.uri(permanent_url(self.entity)),
                      graph.uri(reg.normalize_uri(to_predicate)),
                      graph.uri(permanent_url(related_record)))
        # Export hierarchical relations
        relations_generator = _iter_on_relations(
            self.entity,
            [('reverse_hierarchical_parent', 'hierarchical_child'),
             ('reverse_hierarchical_child', 'hierarchical_parent')])
        self._add_membership_to_graph(graph, self.hierarchical_role, relations_generator,
                                      rtype_to_properties)
        # Export association relations
        relations_generator = _iter_on_relations(
            self.entity,
            [('reverse_association_from', 'association_to'),
             ('reverse_association_to', 'association_from')])
        # As this is an association relation, it makes no sense to have an agent being the
        # organization rather than the other one. That is why we "duplicate" Membership
        # properties: each agent will be both known as a member and an organization.
        relations = list(relations_generator)
        self._add_membership_to_graph(
            graph, self.association_role, relations,
            {'reverse_association_from': ('org:organization', 'org:member'),
             'reverse_association_to': ('org:member', 'org:organization')})
        self._add_membership_to_graph(
            graph, self.association_role, relations,
            {'reverse_association_from': ('org:member', 'org:organization'),
             'reverse_association_to': ('org:organization', 'org:member')})

    def _add_membership_to_graph(self, graph, role, relations, rtype_to_properties):
        reg = self.registry
        for rtype_name, relation, related_record in relations:
            relation_url = permanent_url(relation)
            graph.add(graph.uri(relation_url),
                      graph.uri(reg.normalize_uri(rtype_to_properties[rtype_name][0])),
                      graph.uri(permanent_url(self.entity)))
            graph.add(graph.uri(relation_url),
                      graph.uri(reg.normalize_uri(rtype_to_properties[rtype_name][1])),
                      graph.uri(permanent_url(related_record)))
            graph.add(graph.uri(relation_url),
                      graph.uri(reg.normalize_uri('org:role')),
                      graph.uri(role))
            if relation.start_date or relation.end_date:
                interval_resource = reg.normalize_uri(relation_url + '#timeInterval')
                graph.add(graph.uri(relation_url),
                          graph.uri(reg.normalize_uri('org:memberDuring')),
                          graph.uri(interval_resource))
            if relation.start_date:
                graph.add(graph.uri(interval_resource),
                          graph.uri(reg.normalize_uri('schema_org:startDate')),
                          relation.start_date)
            if relation.end_date:
                graph.add(graph.uri(interval_resource),
                          graph.uri(reg.normalize_uri('schema_org:endDate')),
                          relation.end_date)


def _iter_on_relations(entity, relation_descriptions):
    """yield (rtype_name, relation, related_entity)

    `relation_descriptions` is a list of (rtype_name, reverse_rtype_name)
    """
    for rtype_name, reverse_rtype_name in relation_descriptions:
        for relation in getattr(entity, rtype_name):
            for related_entity in getattr(relation, reverse_rtype_name):
                yield rtype_name, relation, related_entity


_ACTIVITY_ATTRIBUTES = 'cwuri description type start end'.split()


class ConceptSchemeRDFPrimaryAdapter(skos.ConceptSchemeRDFPrimaryAdapter):

    # prefetch 'ark' attribute of concept for RDF export
    skos.ConceptSchemeRDFPrimaryAdapter.concept_attributes.append('ark')

    def register_rdf_mapping(self, reg):
        super(ConceptSchemeRDFPrimaryAdapter, self).register_rdf_mapping(reg)
        _prov_mapping(reg, 'ConceptScheme')

    def accept(self, entity):
        """Return True if the entity should be recursivly added to the graph."""
        return entity.cw_etype == 'Activity'

    def warm_caches(self):
        super(ConceptSchemeRDFPrimaryAdapter, self).warm_caches()
        scheme = self.entity
        cnx = self._cw

        activities, rset = _warm_activity_cache(cnx, scheme, 'CS identity X, A generated X')
        scheme._cw_related_cache['generated_object'] = (rset, activities)
        scheme._cw_related_cache['used_object'] = (rset, activities)

        activities, rset = _warm_activity_cache(cnx, scheme, 'X in_scheme CS, A generated X')
        concepts = tuple(rset.entities(1))
        skos.cache_entities_relations(concepts, rset, 'generated', 'object',
                                      entity_col=0, target_col=1)
        skos.cache_entities_relations(concepts, rset, 'used', 'object',
                                      entity_col=0, target_col=1)


def _warm_activity_cache(cnx, scheme, rql_expr):
    activities_rql = skos._select_attributes(
        'Any X,A WHERE CS eid %(cs)s,' + rql_expr,
        'A', _ACTIVITY_ATTRIBUTES)
    rset = cnx.execute(activities_rql, {'cs': scheme.eid})
    activities = tuple(rset.entities(1))
    skos.cache_entities_relations(activities, rset, 'generated', 'subject')
    skos.cache_entities_relations(activities, rset, 'used', 'subject')
    user_rset = cnx.execute('Any U,A WHERE A associated_with U, CS eid %(cs)s, ' + rql_expr,
                            {'cs': scheme.eid})
    skos.cache_entities_relations(activities, user_rset, 'associated_with', 'subject')
    return activities, rset


class ConceptRDFPrimaryAdapter(skos.ConceptRDFPrimaryAdapter):

    def register_rdf_mapping(self, reg):
        super(ConceptRDFPrimaryAdapter, self).register_rdf_mapping(reg)
        _prov_mapping(reg, 'Concept')

    def accept(self, entity):
        """Return True if the entity should be recursivly added to the graph."""
        return entity.cw_etype == 'Activity'


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, [ConceptSchemeRDFPrimaryAdapter,
                                                     ConceptRDFPrimaryAdapter])
    vreg.register_and_replace(ConceptSchemeRDFPrimaryAdapter, skos.ConceptSchemeRDFPrimaryAdapter)
    vreg.register_and_replace(ConceptRDFPrimaryAdapter, skos.ConceptRDFPrimaryAdapter)
