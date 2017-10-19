# copyright 2015-2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""Utilities for RDF import/export"""

from os.path import abspath, splitext
from urlparse import urlparse

from six import PY2, text_type, string_types

from cubes.skos import POST_321
if POST_321:
    # use new CW 3.21 dataimport API
    from cubicweb.dataimport.importer import ExtEntity
else:
    from cubes.skos import ExtEntity


TYPE_PREDICATE_URI = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
SAME_AS_PREDICATE_URI = 'http://www.w3.org/2002/07/owl#sameAs'


class unicode_with_language(text_type):  # pylint: disable=invalid-name
    """Extend an unicode string to hold a .lang attribute as well"""

    def __new__(cls, content, lang):
        self = text_type.__new__(cls, content)
        self.lang = lang
        return self

    def __repr__(self):
        return '<%r(%s)>' % (super(unicode_with_language, self).__repr__(), self.lang)

    def __eq__(self, other):
        if isinstance(other, unicode_with_language):
            return (text_type(self), self.lang) == (text_type(other), other.lang)
        return False

    def __ne__(self, other):
        return not self == other


def normalize_uri(uri, prefixes, raise_on_error=False):
    """Normalize uri by attempting to substitute prefix by the associated namespace. Returns the
    normalized URI.
    """
    try:
        prefix, value = uri.split(':', 1)
    except ValueError:
        return uri
    try:
        return prefixes[prefix] + value
    except KeyError:
        if raise_on_error:
            raise RDFRegistryError('prefix {0} not found'.format(prefix))
        return uri


def permanent_url(entity):
    """Return permanent URL for the given entity (`<site url>/<eid>`)."""
    return entity._cw.build_url(text_type(entity.eid))


EXTENSION_FORMAT_MAP = {
    '.xml': 'xml',
    '.rdf': 'xml',
    '.rdfs': 'xml',
    '.owl': 'xml',
    '.n3': 'n3',
    '.ttl': 'n3',
    '.nt': 'nt',
    '.trix': 'trix',
    '.xhtml': 'rdfa',
    '.html': 'rdfa',
    '.svg': 'rdfa',
    '.nq': 'nquads',
    '.trig': 'trig'
}


def guess_rdf_format(filename):
    """Return RDF format as detected by the file extension, or raise ValueError if it can't be
    detected.

    Mapping between extension and format is defined in `EXTENSION_FORMAT_MAP` and formats known by
    default are 'xml', 'n3', 'nt', 'trix', 'rdfa', 'nquads'.
    """
    ext = splitext(filename)[1].lower()
    try:
        return EXTENSION_FORMAT_MAP[ext]
    except KeyError:
        raise ValueError("can't guess RDF format for %s, please specify it using "
                         "`rdf_format`" % filename)


class RDFRegistryError(Exception):
    pass


class RDFRegistry(object):
    """Class inspired from yams.xy / cubes.dataio.xy and holding static information about how to
    convert from a Yams model to RDF and the other way around.
    """
    def __init__(self):
        self.prefixes = {}
        self.etype2rdf = {}
        self.attr2rdf = {}
        self.rel2rdf = {}

    def normalize_uri(self, uri, raise_on_error=False):
        return normalize_uri(uri, self.prefixes, raise_on_error=raise_on_error)

    def register_prefix(self, prefix, namespace, overwrite=False):
        """Associate a prefix to a namespace. If the prefix is already registered to a different
        namespace, an exception is raised unless overwrite is True. Registered prefixes may be used
        in RDF snippets used in `register_*` methods.
        """
        if not overwrite and self.prefixes.get(prefix, namespace) != namespace:
            raise RDFRegistryError('prefix %r is already defined with different value %r'
                                   % (prefix, self.prefixes[prefix]))
        self.prefixes[prefix] = namespace

    def register_etype_equivalence(self, etype, rdftype, overwrite=False):
        """Associate a Yams entity type to a RDF type. If the entity type is already registered to a
        different RDF type, an exception is raised unless overwrite is True.
        """
        rdftype = self.normalize_uri(rdftype, raise_on_error=True)
        if not overwrite and self.etype2rdf.get(etype, rdftype) != rdftype:
            raise RDFRegistryError('entity type %r is already associated to RDF type %r'
                                   % (etype, self.etype2rdf[etype]))
        self.etype2rdf[etype] = rdftype

    def register_attribute_equivalence(self, etype, attr, rdftype, overwrite=False):
        """Associate a Yams entity attribute to a RDF predicate. If the entity attribute is already
        registered to a different RDF type, an exception is raised unless overwrite is True.
        """
        rdftype = self.normalize_uri(rdftype, raise_on_error=True)
        if not overwrite and self.attr2rdf.get((etype, attr), rdftype) != rdftype:
            raise RDFRegistryError('entity attribute %s.%r is already associated to RDF type %r'
                                   % (etype, attr, self.attr2rdf[(etype, attr)]))
        self.attr2rdf[(etype, attr)] = rdftype

    def register_relation_equivalence(self, subject_etype, rel, object_etype, rdftype,
                                      reverse=False):
        """Associate a Yams entity relation to a RDF predicated. The `reverse` flag may be used to
        indicate that in RDF, the subject and object are reversed (e.g. 'E1 yams_relation E2' is
        'E2 predicate E1 in RDF').
        """
        rdftype = self.normalize_uri(rdftype, raise_on_error=True)
        self.rel2rdf.setdefault((subject_etype, rel, object_etype), set()).add((rdftype, reverse))

    def predicates_for_subject_etype(self, etype):
        """Given a yams entity type, return (yams relation type, rdf predicate uri, reverse) 3-uple
        where the entity type is subject of the yams relation. `reverse` is a boolean flag telling
        whether the relation should be expected in the opposite direction in RDF (i.e. corresponding
        entity is the object of the rdf predicate), as they are not necessarily in the same order.
        """
        for (subject_etype, attr), rdftype in self.attr2rdf.items():
            if subject_etype == etype:
                yield attr, rdftype, False
        for (subject_etype, rel, _), rdf_relations in self.rel2rdf.items():
            if subject_etype == etype:
                for rdftype, reverse in rdf_relations:
                    yield rel, rdftype, reverse

    def predicates_for_object_etype(self, etype):
        """Given a yams entity type, return (yams relation type, rdf predicate uri, reverse) 3-uple
        where the entity type is object of the yams relation. `reverse` is a boolean flag telling
        wether the relation should be expected in the opposite direction in RDF (i.e. corresponding
        entity is the object of the rdf predicate), as they are not necessarily in the same order.
        """
        for (_, rel, object_etype), rdf_relations in self.rel2rdf.items():
            if object_etype == etype:
                for rdftype, reverse in rdf_relations:
                    yield rel, rdftype, reverse

    def additional_object_predicates(self, etype):
        """Given a yams entity type, return (yams relation type, rdf predicate uri, reverse) 3-uple
        where the entity type is object of the yams relation. `reverse` is a boolean flag telling
        wether the relation should be expected in the opposite direction in RDF (i.e. corresponding
        entity is the object of the rdf predicate), as they are not necessarily in the same order.

        Only relations whose subject is not a registered entity types (i.e. have had a mapping
        registered by :meth:`register_etype_equivalence`) will be returned.
        """
        for (subject_etype, rel, object_etype), rdf_relations in self.rel2rdf.items():
            if object_etype == etype and subject_etype not in self.etype2rdf:
                for rdftype, reverse in rdf_relations:
                    yield rel, rdftype, reverse


class AbstractRDFGraph(object):
    """Abstract base class for RDF graph implementation."""

    _backend_format_map = {}

    @property
    def supported_rdf_formats(self):
        """Return the set of RDF formats supported by the backend."""
        return set(self._backend_format_map)

    @property
    def uri(self):
        """Return the class used to represent URI for the concrete backend."""
        return self._uri_cls

    def load(self, source, rdf_format=None):
        """Add RDF triplets from a file, file path or URL `source` into the graph.

        Allowed values for optional `rdf_format` argument depends on the concret implementation,
        whose supported formats are listed in the `supported_rdf_formats` attribute. If not
        specified, it will be guessed from the file or URL extension.

        Raises `ValueError` if format is unknown or unspecified but can't be guessed.
        """
        if rdf_format is None:
            fname = getattr(source, 'name', source)  # get filename if source is a file.
            rdf_format = guess_rdf_format(fname)
        if rdf_format not in self.supported_rdf_formats:
            raise ValueError('RDF format %r is not supported' % rdf_format)
        self._load(source, self._backend_format_map[rdf_format])

    def _load(self, source, rdf_format):
        raise NotImplementedError

    def dump(self, fobj, rdf_format='xml'):
        """Dump the graph into the given file like object, using `rdf_format` representation.
        Allowed values for the optional `rdf_format` depends on the concret implementation, whose
        supported formats are listed in the `supported_rdf_formats` attribute. If not specified,
        RDF/XML will be used.

        Raises `ValueError` if format is unknown.
        """
        if rdf_format not in self.supported_rdf_formats:
            raise ValueError('RDF format %r is not supported' % rdf_format)
        self._dump(fobj, self._backend_format_map[rdf_format])

    def _dump(self, fobj, rdf_format):
        raise NotImplementedError

    def add(self, subj, predicate, obj):
        """Add statement to graph. subject and predicate are expected to be URIs and object may
        be either a URI or a literal value.
        """
        assert isinstance(subj, self.uri)
        assert isinstance(predicate, self.uri)
        if not isinstance(obj, self.uri):
            if isinstance(obj, unicode_with_language):
                try:
                    obj = self._literal(text_type(obj), lang=obj.lang)
                # an exception may be raised if the library doesn't like specified
                # language (e.g. rdflib check them using a regexp), but we don't
                # know at this point which kind of exception so catch Exception
                except Exception:
                    obj = self._literal(obj)
            else:
                obj = self._literal(obj)
        self._add(subj, predicate, obj)

    def _add(self, subj, predicate, obj):
        raise NotImplementedError


class LibRDFRDFGraph(AbstractRDFGraph):
    """redland's librdf based RDF graph"""
    _backend_format_map = {'nt': 'ntriples',
                           'n3': 'turtle',
                           'xml': 'rdfxml',
                           }
    _py_xsd_map = {
        int: 'http://www.w3.org/2001/XMLSchema#integer',
    }
    if PY2:
        _py_xsd_map[long] = 'http://www.w3.org/2001/XMLSchema#long'  # noqa

    _xsd_py_map = dict((v, k) for k, v in _py_xsd_map.items())

    def __init__(self, options_string="new='yes',hash-type='memory',dir='.'"):
        import RDF
        self._uri_cls = RDF.Uri
        storage = RDF.HashStorage("test", options_string)
        self._model = RDF.Model(storage)
        self._parser = RDF.Parser
        self._serializer = RDF.Serializer
        self._stmt = RDF.Statement
        node = RDF.Node
        self._node = node
        self._uri_node = lambda x: node(uri=x) if isinstance(x, RDF.Uri) else node(uri_string=x)

    def _load(self, source, rdf_format):
        """Add RDF triplets from a file path or URL into the graph."""
        assert isinstance(source, string_types), \
            '{0}._load() expect a path or an URL as source'.format(self.__class__.__name__)
        if ':/' not in source:
            source = 'file://' + abspath(source)
        parser = self._parser(name=rdf_format)
        parser.parse_into_model(self._model, self.uri(string=source))
        self._model.sync()  # in case model use a persistent storage

    def _dump(self, fobj, rdf_format):
        """Dump the graph into the given file like object, using `rdf_format` representation.
        """
        serializer = self._serializer(name=rdf_format)
        fobj.write(serializer.serialize_model_to_string(self._model))

    def _add(self, subj, predicate, obj):
        """Add RDF triplet to the graph."""
        self._model.add_statement(self._stmt(subj, predicate, obj))

    def _literal(self, value, lang=None):
        """Given a typed python value return proper RDFLib node."""
        if lang is None:
            try:
                datatype = self._py_xsd_map[type(value)]
            except KeyError:
                return self._node(literal=text_type(value))
            else:
                datatype = self.uri(datatype)
                return self._node(literal=text_type(value), datatype=datatype)
        return self._node(literal=value, language=str(lang))

    def _py_literal(self, node):
        """Given a RDFLib node return a typed python value."""
        try:
            string_value, language, datatype_uri = node.literal
        except AttributeError:
            # old librdf/redland version (e.g. centos6 has 1.0.7.1)
            string_value = node.literal_value['string']
            language = node.literal_value['language']
            datatype_uri = node.literal_value['datatype']
        if language is not None:
            return unicode_with_language(string_value, language)
        if datatype_uri is not None:
            datatype_uri = str(datatype_uri)
            if datatype_uri in self._xsd_py_map:
                return self._xsd_py_map[datatype_uri](string_value)
        return string_value

    def uris_for_type(self, type_uri):
        """Yield URIs of the given RDF type"""
        qs = self._stmt(subject=None,
                        predicate=self._uri_node(TYPE_PREDICATE_URI),
                        object=self._uri_node(type_uri))
        for statement in self._model.find_statements(qs):
            yield str(statement.subject.uri)

    def triples(self):
        """Yield every triples in the graph."""
        qs = self._stmt(subject=None, predicate=None, object=None)
        for statement in self._model.find_statements(qs):
            subject = str(statement.subject.uri)
            predicate = str(statement.predicate.uri)
            object = statement.object
            if object.is_literal():
                object = self._py_literal(statement.object)
            elif object.is_blank():
                object = str(statement.object.blank_identifier)
            else:
                object = str(statement.object.uri)
            yield subject, predicate, object

    def objects(self, entity_uri, predicate_uri):
        """Yield object URIs or literals that are linked to `entity_uri` through
        `predicate_uri`.
        """
        qs = self._stmt(subject=self._uri_node(entity_uri),
                        predicate=self._uri_node(predicate_uri),
                        object=None)
        for statement in self._model.find_statements(qs):
            if statement.object.is_literal():
                yield self._py_literal(statement.object)
            elif statement.object.is_blank():
                yield str(statement.object.blank_identifier)
            else:
                yield str(statement.object.uri)

    def subjects(self, predicate_uri, entity_uri):
        """Yield subject URIs that are linked to `entity_uri` through
        `predicate_uri`.
        """
        qs = self._stmt(subject=None,
                        predicate=self._uri_node(predicate_uri),
                        object=self._uri_node(entity_uri))
        for statement in self._model.find_statements(qs):
            yield str(statement.subject.uri)


class RDFLibRDFGraph(AbstractRDFGraph):
    """rdflib based RDF graph (http://rdflib.readthedocs.org)"""
    _backend_format_map = dict((x, x) for x in ('xml', 'n3', 'nt', 'rdfa'))
    _backend_format_map['pretty-xml'] = 'xml'

    def __init__(self):
        import rdflib
        self._uri_cls = rdflib.URIRef
        self._namespace = rdflib.namespace
        self._literal = rdflib.Literal
        self._graph = rdflib.ConjunctiveGraph()
        from rdflib.plugin import register, Parser
        register('text/rdf+n3', Parser, 'rdflib.plugins.parsers.notation3', 'N3Parser')

    def _load(self, source, rdf_format=None):
        """Add RDF triplets from a file stream, path or URL into the graph. `rdf_format` may be one
        of 'nt', 'n3' or 'xml'. If not specified, it will be guessed from the file or URL extension.
        """
        self._graph.parse(source, format=rdf_format)

    def _dump(self, fobj, rdf_format):
        """Dump the graph into the given file like object, using `rdf_format` representation.
        """
        self._graph.serialize(fobj, format=rdf_format)

    def _add(self, subj, predicate, obj):
        """Add RDF triplet to the graph."""
        self._graph.add((subj, predicate, obj))

    def uris_for_type(self, type_uri):
        """Return an iterator on URIs of the given RDF type"""
        for subj in self._graph.subjects(self._namespace.RDF.type, self.uri(type_uri)):
            yield text_type(subj)

    def triples(self):
        """Yield every triples in the graph."""
        for subj, pred, obj in self._graph.triples((None, None, None)):
            if isinstance(obj, self.uri):
                obj = text_type(obj)
            elif getattr(obj, 'language', None) is not None:
                obj = unicode_with_language(obj.toPython(), obj.language)
            else:
                obj = obj.toPython()
            yield text_type(subj), text_type(pred), obj

    def objects(self, entity_uri, predicate_uri):
        """Return an iterator on object URIs or literals that are linked to `entity_uri` through
        `predicate_uri`.
        """
        for obj in self._graph.objects(self.uri(entity_uri), self.uri(predicate_uri)):
            if isinstance(obj, self.uri):
                yield text_type(obj)
            elif getattr(obj, 'language', None) is not None:
                yield unicode_with_language(obj.toPython(), obj.language)
            else:
                yield obj.toPython()

    def subjects(self, predicate_uri, entity_uri):
        """Return an iterator on subject URIs that are linked to `entity_uri` through
        `predicate_uri`.
        """
        for subj in self._graph.subjects(self.uri(predicate_uri), self.uri(entity_uri)):
            yield text_type(subj)


def default_graph():
    """Return a default graph instance depending on installed software."""
    try:
        return RDFLibRDFGraph()
    except ImportError:
        try:
            return LibRDFRDFGraph()
        except ImportError:
            raise ValueError('neither rdflib nor RDF library installed')


def rdf_graph_to_entities(reg, graph, etypes, output_cls=ExtEntity):
    """Turns RDF data into an transitional ExtEntity representation that may
    be then imported into some database easily.

    Mapping is done using a RDF registry `reg` (see :class:`RDFRegistry`).
    """
    for etype in etypes:
        type_uri = reg.etype2rdf[etype]
        for uri in graph.uris_for_type(type_uri):
            extentity = output_cls(etype, uri)
            for rtype, predicate_uri, reverse in reg.predicates_for_subject_etype(etype):
                if reverse:
                    uris = graph.subjects(predicate_uri, uri)
                else:
                    uris = graph.objects(uri, predicate_uri)
                uris = set(uris)  # may be a generator
                if uris:
                    extentity.values[rtype] = uris
            for rtype, predicate_uri, reverse in reg.additional_object_predicates(etype):
                if reverse:
                    uris = graph.objects(uri, predicate_uri)
                else:
                    uris = graph.subjects(predicate_uri, uri)
                uris = set(uris)  # may be a generator
                if uris:
                    extentity.values[rtype] = uris
            yield extentity


def entities_stack(entities):
    """Coroutine function responsible for yielding entities from a stack of unique
    values that can be updated by calling the `send()` method.
    """
    entities = set(entities)
    processed = set()
    while entities:
        current = entities.pop()
        newones = yield current
        processed.add(current.eid)
        if newones:
            # Update the "stack" with new inputs.
            entities.update(x for x in newones if x.eid not in processed)


class RDFGraphGenerator(object):
    """RDF Graph generator using an RDF graph implementation.

    Fill the graph by calling `add_entity` with each entity to add to the graph.
    """
    def __init__(self, graph):
        self._graph = graph
        self._type_predicate = graph.uri(TYPE_PREDICATE_URI)
        self._same_as_predicate = graph.uri(SAME_AS_PREDICATE_URI)

    @classmethod
    def same_as_uris(cls, entity):
        """Return URIs of the given entity that should be linked using the `same_as` relation."""
        if urlparse(cls.canonical_uri(entity)).netloc != urlparse(entity.cwuri).netloc:
            yield entity.cwuri

    @staticmethod
    def canonical_uri(entity):
        """Return URIs of the given entity that should be linked using the `same_as` relation."""
        return permanent_url(entity)

    def add_entity(self, entity, reg):
        """Add information about a single entity as defined in the given RDF registry into the RDF
        graph and return related entities for eventual further processing.
        """
        graph = self._graph
        etype = entity.cw_etype
        if etype not in reg.etype2rdf:
            return ()
        uri = graph.uri(self.canonical_uri(entity))
        graph.add(uri, self._type_predicate, graph.uri(reg.etype2rdf[etype]))
        for same_as_uri in self.same_as_uris(entity):
            graph.add(uri, self._same_as_predicate, graph.uri(same_as_uri))
        related = set()
        for rtype, predicate_uri, reverse in reg.predicates_for_subject_etype(etype):
            if callable(rtype):
                values = rtype(entity)
            else:
                values = getattr(entity, rtype)
            if values is None:
                continue
            if isinstance(values, (tuple, list)):  # relation
                self._add_relations(uri, predicate_uri, reverse, values)
                related.update(values)
            else:  # attribute.
                assert not reverse, (uri, rtype, predicate_uri, reverse)
                graph.add(uri, graph.uri(predicate_uri), values)
        for rtype, predicate_uri, reverse in reg.predicates_for_object_etype(etype):
            try:
                values = getattr(entity, 'reverse_' + rtype)
            except AttributeError:
                # symmetric relations have no 'reverse_' attribute
                # XXX what if this is simply a bad mapping?
                continue
            related.update(values)
            self._add_relations(uri, predicate_uri, not reverse, values)
        return related

    def _add_relations(self, uri, predicate_uri, reverse, related_entities):
        """Add information about relations with `predicate_uri` between entity with `uri` and
        `related_entities` to the graph.
        """
        graph = self._graph
        predicate = graph.uri(predicate_uri)
        for related_entity in related_entities:
            r_uri = graph.uri(self.canonical_uri(related_entity))
            if reverse:
                graph.add(r_uri, predicate, uri)
            else:
                graph.add(uri, predicate, r_uri)
