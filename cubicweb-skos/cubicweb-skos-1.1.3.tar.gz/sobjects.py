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
"""SKOS import is available through:

* a c-c command
* a repository service
* the datafeed source API

The first two will create local entities (i.e. whose `cw_source` relation points to system source)
while the last will create entities belonging to the external source.

This file contains generic import code, the datafeed parser and the repository service.
"""

from hashlib import md5
from uuid import uuid4
from itertools import imap

from logilab.common.deprecation import deprecated

from cubicweb import schema, dataimport
from cubicweb.predicates import match_kwargs, match_user_groups
from cubicweb.server import Service
from cubicweb.server.sources import datafeed

from cubes.skos import (POST_321, LABELS_RDF_MAPPING, register_skos_rdf_input_mapping,
                        rdfio, lcsv, to_unicode)


def ext_dump_relations(cnx, extid2eid, extentity):
    """Wrapper around :func:`dump_relations` but receiving extentity and extdid2eid mapping as
    argument, to attempt to work around store's limitation on inlined relation.
    """
    eid = extid2eid[extentity.extid]
    etype = cnx.entity_metas(eid)['type']
    relations = []
    rschema = cnx.vreg.schema.rschema
    for subj, rtype, obj in dump_relations(cnx, eid, etype):
        if rschema(rtype).inlined:
            if subj is None:
                if obj is None:
                    obj = extentity.extid
                else:
                    extid2eid[obj] = obj
                extentity.values.setdefault(rtype, set()).add(obj)
            else:
                raise Exception("can't dump inlined object relation {0}".format(rtype))
        else:
            relations.append((subj, rtype, obj))
    return relations


def dump_relations(cnx, eid, etype):
    """Return a list of relation 3-uples `(subject_eid, relation, object_eid)` with None instead of
    `subject_eid` or `object_eid` depending on whether the entity type corresponding to `eid` is
    subject or object.
    """
    eschema = cnx.vreg.schema.eschema(etype)
    relations = []
    for rschema, _, role in eschema.relation_definitions():
        if rschema.rule:  # computed relation
            continue
        rtype = rschema.type
        if rtype in schema.VIRTUAL_RTYPES or rtype in schema.META_RTYPES:
            continue
        if role == 'subject':
            for object_eid, in cnx.execute('Any Y WHERE X %s Y, X eid %%(x)s' % rtype, {'x': eid}):
                if object_eid == eid:
                    object_eid = None
                relations.append((None, rtype, object_eid))
        else:
            for subject_eid, in cnx.execute('Any Y WHERE Y %s X, X eid %%(x)s' % rtype, {'x': eid}):
                if subject_eid == eid:
                    subject_eid = None
                relations.append((subject_eid, rtype, None))
    return relations


class RDFSKOSImportService(Service):
    """CubicWeb service to import a ConceptScheme from SKOS RDF."""

    __regid__ = 'rdf.skos.import'
    __select__ = match_kwargs('stream') & match_user_groups('managers')

    def call(self, stream, **kwargs):
        import_log = HTMLImportLog(getattr(stream, 'filename', u''))
        (created, updated), scheme_uris = self._do_import(stream, import_log, **kwargs)
        import_log.record_info('%s entities created' % len(created))
        import_log.record_info('%s entities updated' % len(updated))
        self._cw.commit()
        return import_log.logs, scheme_uris

    # Extracted method to let a chance to client cubes to give more arguments to
    # import_skos_extentities function
    def _do_import(self, stream, import_log, rdf_format=None, **kwargs):
        entities = rdf_extentities(stream, rdf_format)
        return import_skos_extentities(self._cw, entities, import_log, **kwargs)


class LCSVSKOSImportService(RDFSKOSImportService):
    """CubicWeb service to import a Concept and Label entities from LCSV file into a pre-existing
    ConceptScheme.
    """
    __regid__ = 'lcsv.skos.import'

    # Extracted method to let a chance to client cubes to give more arguments to
    # import_skos_extentities function
    def _do_import(self, stream, import_log,
                   scheme_uri, delimiter, encoding, language_code=None,
                   **kwargs):
        entities = lcsv_extentities(stream, scheme_uri, delimiter, encoding, language_code)
        return import_skos_extentities(self._cw, entities, import_log,
                                       extid_as_cwuri=False, **kwargs)


class SKOSParser(datafeed.DataFeedParser):
    """CubicWeb parser to import a ConceptScheme from SKOS RDF."""
    __regid__ = 'rdf.skos'

    def process(self, url, raise_on_error=False):
        """Main entry point"""
        try:
            created, updated = self._do_import(url, raise_on_error=raise_on_error)[0]
        except Exception as ex:
            if raise_on_error:
                raise
            self.exception('error while importing %s', url)
            self.import_log.record_error(to_unicode(ex))
            return True
        self.stats['created'] = created
        self.stats['updated'] = updated
        return False

    # Extracted method to let a chance to client cubes to give more arguments to
    # import_skos_extentities function
    def _do_import(self, url, raise_on_error, **kwargs):
        try:
            rdf_format = rdfio.guess_rdf_format(url)
        except ValueError:
            rdf_format = 'xml'
        entities = rdf_extentities(url, rdf_format)
        return import_skos_extentities(self._cw, entities, self.import_log,
                                       source=self.source, raise_on_error=raise_on_error, **kwargs)


def lcsv_extentities(stream, scheme_uri, delimiter, encoding, language_code=None):
    """Return external entities generator from SKOS LCSV stream or URL (by transforming it to RDF
    first).

    Arguments:

    * `stream`, stream of the LCSV data
    * `scheme_uri`, cwuri of  the scheme into which imported concepts will be inserted
    * `delimiter`, CSV delimiter character
    * `encoding`, encoding of the CSV file
    * `language_code`, default language code of labels, in case it's not specified along the label
      definition
    """
    graph = rdfio.RDFLibRDFGraph()
    # add LCSV statements to the RDF graph
    lcsv2rdf = lcsv.LCSV2RDF(stream, delimiter, encoding, default_lang=language_code,
                             uri_cls=graph.uri, uri_generator=lambda x: str(uuid4()) + x)
    for (subj, pred, obj) in lcsv2rdf.triples():
        graph.add(subj, pred, obj)

    # we need an extra transform that link Concept to the parent concept skeme
    def relate_concepts(extentity):
        """Relate Concept ExtEntities to the ConceptScheme"""
        if extentity.etype == 'Concept':
            extentity.values.setdefault('in_scheme', set([])).add(scheme_uri)
        return extentity

    return imap(relate_concepts, graph_extentities(graph))


def rdf_extentities(stream_or_url, rdf_format=None):
    """Return external entities generator from SKOS RDF stream or URL.

    Arguments:

    * `stream_or_url`, stream or URL of the RDF data

    * `rdf_format`, RDF format used to defined the data. See formats supported by
      :class:`RDFLibRDFGraph`. If not specified, it will be guessed from the URL extension or
      default to xml
    """
    graph = rdfio.RDFLibRDFGraph()
    graph.load(stream_or_url, rdf_format)
    return graph_extentities(graph)


def graph_extentities(graph):
    """Return external entities generator from a RDF graph implementation (i.e. instance
    implementing :class:`cubes.skos.rdfio.AbstractRDFGraph`).
    """
    reg = rdfio.RDFRegistry()
    register_skos_rdf_input_mapping(reg)
    all_label_rtypes = frozenset(LABELS_RDF_MAPPING)
    # transform direct mapping of RDF as ExtEntity into Yams compatible ExtEntity by turning label
    # literals into entities.
    for extentity in rdfio.rdf_graph_to_entities(reg, graph, ('ConceptScheme', 'Concept')):
        label_rtypes = frozenset(extentity.values) & all_label_rtypes
        if not label_rtypes:
            yield extentity
            continue
        labels = []
        for rtype in label_rtypes:
            kind = rtype.split('_', 1)[0]  # drop '_label' suffix
            for label in extentity.values.pop(rtype):
                lang = getattr(label, 'lang', None)
                md5hash = md5(str(lang) + label.encode('utf-8'))
                labelid = str(extentity.extid) + '#' + rtype + md5hash.hexdigest()
                labels.append(ExtEntity('Label', labelid,
                                        {'label': set([label]),
                                         'language_code': set([lang]),
                                         'kind': set([kind]),
                                         'label_of': set([extentity.extid])}))
        # yield extentity before labels since it must be handled first in case the ExternalUri
        # to Concept transformation apply
        yield extentity
        for label in labels:
            yield label


def import_skos_extentities(cnx, entities, import_log,
                            source=None, metagenerator=None, store=None, **kwargs):
    """Import SKOS external entities.

    Arguments:

    * `cnx`, RQL connection to the CubicWeb instance
    * `entities`, iterable (usualy a generator) on external entities to import
    * `import_log`, import log instance to give to the store
    * `source`, optional source in which existing entities will be looked for
      (default to the system source); if store and metagenerator are
      unspecified, imported entities will be attached to this source,
      otherwise make sure the source declared in store/metagenerator is
      consistent with this one
    * `metagenerator`, metadata generator to be given to the store if store isn't specified
    * `store`, store to use for the import

    Extra arguments will be given to :func:`store_skos_extentities` function.
    """
    # By default, use NoHookRQLObjectStore for insertion in the database, with a custom
    # metagenerator to properly set the source for created entities
    if store is None:
        if metagenerator is None:
            metagenerator = dataimport.MetaGenerator(cnx, source=source)
        store = dataimport.NoHookRQLObjectStore(cnx, metagenerator)
    else:
        assert metagenerator is None, 'you should not give both a store and a metadata generator'
    res = store_skos_extentities(cnx, store, entities, import_log, source, **kwargs)
    store.flush()
    store.commit()
    if hasattr(store, 'finish'):  # XXX not all store have this before cw 3.22
        store.finish()
    return res


if POST_321:
    # use new CW 3.21 dataimport API
    from .post321_import import HTMLImportLog, ExtEntity, store_skos_extentities
else:
    from .pre321_import import HTMLImportLog, ExtEntity, store_skos_extentities


@deprecated('[skos 0.9] use lcsv_extentities then import_skos_extentities instead')
def _skos_import_lcsv(cnx, stream, import_log, scheme_uri, delimiter,
                      encoding, language_code=None, **kwargs):
    """Import SKOS from LCSV stream or URL (by transforming it to RDF first)."""
    entities = lcsv_extentities(stream, scheme_uri, delimiter, encoding, language_code)
    return import_skos_extentities(cnx, entities, import_log, extid_as_cwuri=False, **kwargs)


@deprecated('[skos 0.9] use rdf_extentities then import_skos_extentities instead')
def _skos_import_rdf(cnx, stream_or_url, import_log, rdf_format=None, **kwargs):
    """Import SKOS from RDF stream or URL."""
    entities = rdf_extentities(stream_or_url, rdf_format)
    return import_skos_extentities(cnx, entities, import_log, **kwargs)
