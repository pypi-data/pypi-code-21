# copyright 2015-2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-skos entity classes"""

from itertools import ifilter

from logilab.common.decorators import cachedproperty

from cubicweb.predicates import is_instance
from cubicweb.view import EntityAdapter
from cubicweb.entities import AnyEntity, fetch_config
from cubicweb.entities.adapters import ITreeAdapter

from cubes import skos
from cubes.skos import rdfio
from cubes.skos.rdfio import unicode_with_language as ul


def _add_concept(scheme, label, language_code, kind=u'preferred', **kwargs):
    cnx = scheme._cw
    concept = cnx.create_entity('Concept', in_scheme=scheme, **kwargs)
    cnx.create_entity('Label', label=label, language_code=language_code,
                      kind=kind, label_of=concept)
    # hooks do use existing labels, clear cache here to ensure the label is considered
    concept.cw_clear_all_caches()
    return concept


class CSVParseError(Exception):
    """Error during CSV parsing, with a line information."""

    def __init__(self, line):
        super(CSVParseError, self).__init__()
        self.line = line


class CSVIndentationError(CSVParseError):
    """Invalid indentation (level was reduced by more than one indentation)."""


class CSVDecodeError(CSVParseError):
    """Decode exception, probably due to a wrongly specified encoding."""


class ConceptScheme(AnyEntity):
    __regid__ = 'ConceptScheme'
    fetch_attrs, cw_fetch_order = fetch_config(('title', 'cwuri'))

    def dc_title(self):
        if self.title:
            return self.title
        return self.cwuri

    @cachedproperty
    def top_concepts_rset(self):
        return self._cw.execute(
            'Any C,CU WHERE C cwuri CU, C in_scheme X, NOT C broader_concept SC, X eid %(x)s',
            {'x': self.eid})

    @property
    def top_concepts(self):
        return list(self.top_concepts_rset.entities())

    def add_concept(self, label, language_code=u'en', kind=u'preferred', **kwargs):
        """Add a top-concept to this scheme"""
        return _add_concept(self, label, language_code, kind, **kwargs)

    def add_concepts_from_file(self, stream, encoding, language_code, delimiter):
        """Read a stream and create the listed concepts inside the ConceptScheme

        'delimiters' are considered as hierarchical information. There must be a concept per line,
        each line starting by N delimiters (indicating the hierarchical level) or nothing if the
        concept has no parent.

        Example (delimiter = u';')
        titi
        ;toto
        ;;tata
        --> ok: titi is a top-concept of the scheme, toto is a narrower concept of titi, tata is a
        narrower concept of toto

        titi
         ;toto
        --> 'titi' and ' ;toto' will be considered as two concepts of the scheme.
        """
        # This ordered list behaves like a state machine. It will contain all the concepts from
        # the conceptscheme to the more recent broader concept. The last element is consequently
        # the current parent concept. When de-indenting, the concepts are popped.
        level = -1
        broaderconcepts = [(self, level)]
        for nline, line in enumerate(stream, 1):
            try:
                line = line.rstrip().decode(encoding)
            except UnicodeDecodeError:
                raise CSVDecodeError(nline)
            if not line:
                continue
            # Find the label by removing leading delimiters (and spaces), then
            # remove trailing delimiters and spaces.
            label = line.lstrip(delimiter + ' ').rstrip(delimiter + ' ')
            if not label:
                # The line is full of delimiter.
                continue
            next_level = line[:line.index(label)].count(delimiter)
            if next_level - level > 1:
                # Concept must be at much one level below its parent.
                raise CSVIndentationError(nline)
            elif next_level <= level:
                # Walk back levels.
                while next_level <= level:
                    _, level = broaderconcepts.pop()
            concept = broaderconcepts[-1][0].add_concept(label, language_code)
            broaderconcepts.append((concept, level))
            level = next_level


class Concept(AnyEntity):
    __regid__ = 'Concept'
    fetch_attrs, cw_fetch_order = fetch_config(('cwuri',))

    def dc_title(self):
        return self.label()

    @property
    def parent_concept(self):
        return self.broader_concept[0] if self.broader_concept else None

    @property
    def scheme(self):
        return self.in_scheme[0]

    @property
    def labels(self):
        """Dict of preferred labels by (short) language-code."""
        labels = {}
        for l in self.preferred_label:
            labels[l.short_language_code] = l.label
            labels[l.language_code] = l.label
        return labels

    def label(self, language_code=None, default_language_code='en'):
        if language_code is None:
            language_code = self._cw.lang
        for possible_lang in (language_code, language_code[:2], default_language_code[:2]):
            # First try to find a preferred label matching requested language.
            try:
                return self.labels[language_code.lower()]
            except KeyError:
                continue
        else:
            # Else pick a preferred label in any language.
            return self.labels.values()[0]

    def add_concept(self, label, language_code=u'en', kind=u'preferred'):
        """Add a sub-concept to this concept"""
        return _add_concept(self.scheme, label, language_code, kind, broader_concept=self)


class Label(AnyEntity):
    __regid__ = 'Label'
    fetch_attrs, cw_fetch_order = fetch_config(('language_code', 'label', 'kind'))

    @property
    def short_language_code(self):
        """Return the 2 letters language code for this label"""
        if self.language_code is None:
            return None
        return self.language_code[:2].lower()


class ConceptITreeAdapter(ITreeAdapter):
    """ITree adapater for Concept"""
    __select__ = is_instance('Concept')
    tree_relation = 'broader_concept'


class AbstractRDFAdapter(EntityAdapter):
    """Abstract RDF adapter, providing helper methods easing usage of :class:rdfio.RDFRegistry to
    generate (part of) the graph.
    """
    __abstract__ = True

    @cachedproperty
    def registry(self):
        """Return the RDFRegistry to be used for RDF serialisation."""
        reg = rdfio.RDFRegistry()
        self.register_rdf_mapping(reg)
        return reg

    def register_rdf_mapping(self, reg):
        """Add mapping RDF serialisation to the given registry."""
        raise NotImplementedError

    def accept(self, entity):
        """Return True if the entity should be recursivly added to the graph."""
        return False

    def add_entities_to_rdf_graph(self, graph):
        """Add entities mapped in the registry to the RDF graph."""
        stack = rdfio.entities_stack([self.entity])
        generator = rdfio.RDFGraphGenerator(graph)
        related = None
        try:
            while True:
                # Send the list of related entities to process (encountered
                # during previous iterations) to the stack and retrieve one
                # entity to add to the graph.
                entity = stack.send(related)
                related = generator.add_entity(entity, self.registry)
                related = ifilter(self.accept, related)
        except StopIteration:
            return

    def fill(self, graph):
        """Adapter entry point, for use in RDF views."""
        self.add_entities_to_rdf_graph(graph)


class ConceptRDFListAdapter(AbstractRDFAdapter):
    """The RDFList adapter for Concept entity type."""

    __regid__ = 'RDFList'
    __select__ = is_instance('Concept')
    register_rdf_mapping = staticmethod(skos.register_skos_concept_rdf_list_mapping)


class ConceptRDFPrimaryAdapter(AbstractRDFAdapter):
    """The RDFList adapter for Concept entity type."""

    __regid__ = 'RDFPrimary'
    __select__ = is_instance('Concept')
    register_rdf_mapping = staticmethod(skos.register_skos_concept_rdf_output_mapping)

    def fill(self, graph):
        super(ConceptRDFPrimaryAdapter, self).fill(graph)
        reg = self.registry
        concept = self.entity
        concept_uri = graph.uri(rdfio.RDFGraphGenerator.canonical_uri(concept))
        # manually handle labels to provide string with language code
        for rtype in skos.LABELS_RDF_MAPPING:
            skos_rel = graph.uri(reg.normalize_uri(skos.LABELS_RDF_MAPPING[rtype]))
            for label in getattr(concept, rtype):
                graph.add(concept_uri, skos_rel, ul(label.label, label.language_code))


class ConceptSchemeRDFListAdapter(AbstractRDFAdapter):
    """The RDFList adapter fill the RDF graph with a short representation of the adapted entity, for
    use with the 'list.rdf' view.
    """
    __regid__ = 'RDFList'
    __select__ = is_instance('ConceptScheme')

    register_rdf_mapping = staticmethod(skos.register_skos_rdf_list_mapping)


class ConceptSchemeRDFPrimaryAdapter(AbstractRDFAdapter):
    """The RDFPrimary adapter fill the RDF graph with a short representation of the adapted entity,
    for use with the 'primary.rdf' view.
    """
    __regid__ = 'RDFPrimary'
    __select__ = is_instance('ConceptScheme')

    register_rdf_mapping = staticmethod(skos.register_skos_rdf_output_mapping)

    def fill(self, graph):
        # prefill entity cache
        self.warm_caches()
        self.add_entities_to_rdf_graph(graph)
        for concept in self.entity.reverse_in_scheme:
            concept.cw_adapt_to('RDFPrimary').fill(graph)

    concept_attributes = 'cwuri definition example'.split()
    label_attributes = 'label language_code'.split()

    def warm_caches(self):
        scheme = self.entity
        cnx = self._cw
        scheme.complete()
        concept_rql = _select_attributes('Any CS,C WHERE C in_scheme CS, CS eid %(cs)s',
                                         'C', self.concept_attributes)
        rset = cnx.execute(concept_rql, {'cs': scheme.eid})
        concepts = tuple(rset.entities(1))
        cache_entities_relations(concepts, rset, 'in_scheme', 'subject')
        scheme._cw_related_cache['in_scheme_object'] = (rset, concepts)
        for rtype in skos.LABELS_RDF_MAPPING:
            label_rql = 'Any L,C WHERE C %s L, C in_scheme CS, CS eid %%(cs)s' % rtype
            label_rql = _select_attributes(label_rql, 'L', self.label_attributes)
            rset = cnx.execute(label_rql, {'cs': scheme.eid})
            cache_entities_relations(concepts, rset, rtype, 'subject')
        for rtype in ('exact_match', 'close_match'):
            rset = cnx.execute('Any X,C,XU WHERE C %s X?, C in_scheme CS, CS eid %%(cs)s, '
                               'X cwuri XU' % rtype, {'cs': scheme.eid})
            cache_entities_relations(concepts, rset, rtype, 'subject')
        for rtype in ('broader_concept', 'related_concept'):
            rset = cnx.execute('Any C1,C2 WHERE C1 %s C2, C1 in_scheme CS, C2 in_scheme CS, '
                               'CS eid %%(cs)s' % rtype, {'cs': scheme.eid})
            cache_entities_relations(concepts, rset, rtype, 'subject', 0, 1)
            if rtype == 'broader_concept':
                cache_entities_relations(concepts, rset, rtype, 'object', 1, 0)


def _select_attributes(rql, var, attributes):
    assert attributes
    select, where = rql.split(' WHERE ')
    for iattr, attr in enumerate(attributes):
        attrvar = '%s%s' % (var, iattr)
        where += ', %s %s %s' % (var, attr, attrvar)
        select += ', %s' % attrvar
    return '%s WHERE %s' % (select, where)


def _split_rset(rset, entity_col):
    syntax_tree = rset.syntax_tree()
    syntax_tree.copy = lambda: syntax_tree  # avoid extra copy()
    for entity, subrset in rset.split_rset(col=entity_col, return_dict=True).iteritems():
        subrset._rqlst = syntax_tree
        yield entity, subrset


def cache_entities_relations(entities, rset, rtype, role, entity_col=1, target_col=0):
    """Warm entity relation cache for `rtype` / `role` according to the given rset. This is usually
    useful for multi-valued relations that are not well handled by the ORM by default.

    * `entities` is the list of entities whose cache is expected to be warmed - entities which are
      not found in the `entity_col` column of the rset will have their cache set to an empty rset

    * related entities are in `target_col` column of the rset
    """
    no_relation = set(entities)
    cache_key = '%s_%s' % (rtype, role)
    for entity, subrset in _split_rset(rset, entity_col):
        entity._cw_related_cache[cache_key] = (subrset, tuple(subrset.entities(target_col)))
        try:
            no_relation.remove(entity)
        except KeyError:
            continue
    if no_relation:
        empty_rset = rset.req.empty_rset()
        for entity in no_relation:
            entity._cw_related_cache[cache_key] = (empty_rset, ())
