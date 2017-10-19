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
"""SKOS Import code specific to cubicweb >= 3.21"""

from itertools import imap

from six import text_type

from cubicweb.dataimport.importer import (ExtEntity, ExtEntitiesImporter, RelationMapping,
                                          cwuri2eid, use_extid_as_cwuri)
from cubicweb.dataimport.importer import HTMLImportLog  # noqa

from cubes.skos.sobjects import ext_dump_relations


class SKOSRelationMapping(RelationMapping):

    def __getitem__(self, rtype):
        if rtype in ('exact_match', 'close_match'):
            rql = 'Any S,O WHERE S {0} O'.format(rtype)
            return set(tuple(x) for x in self.cnx.execute(rql))
        return super(SKOSRelationMapping, self).__getitem__(rtype)


def store_skos_extentities(cnx, store, entities, import_log,
                           source=None, raise_on_error=False,
                           extid2eid=None, extid_as_cwuri=True):
    """Add SKOS external entities to the store. Don't commit/flush any data.

    Arguments:

    * `cnx`, RQL connection to the CubicWeb instance
    * `store`, store to use for the import
    * `entities`, iterable (usualy a generator) on external entities to import
    * `import_log`, import log instance to give to the store
    * `source`, optional source in which existing entities will be looked for
      (default to the system source)
    * `raise_on_error`, boolean flag telling if we should fail on error or simply log it (default
      to `False`)
    * `extid_as_cwuri`, boolean flag telling if we should use the external entities'extid as `cwuri`
      attribute of imported entities (default to `True`)
    """
    # only consider the system source for schemes and labels
    if source is None:
        source_eid = cnx.repo.system_source.eid
    else:
        source_eid = source.eid
    if extid2eid is None:
        extid2eid = cwuri2eid(cnx, ('ConceptScheme', 'Label'), source_eid=source_eid)
        # though concepts and external URIs may come from any source
        extid2eid.update(cwuri2eid(cnx, ('Concept', 'ExternalUri')))
    # plug function that turn previously known external uris by newly inserted concepts
    restore_relations = {}

    # pylint: disable=dangerous-default-value
    def externaluri_to_concept(extentity, cnx=cnx, extid2eid=extid2eid,
                               restore_relations=restore_relations):
        try:
            eid = extid2eid[extentity.extid]
        except KeyError:
            pass
        else:
            if extentity.etype == 'Concept' and cnx.entity_metas(eid)['type'] == 'ExternalUri':
                # We have replaced the external uri by the new concept. As entities.extid column is
                # unique, we've to drop the external uri before inserting the concept, so we:
                #  1. record every relations from/to the external uri,
                #  2. remove it,
                #  3. insert the concept and
                #  4. reinsert relations using the concept instead
                #
                # 1. record relations from/to the external uri
                restore_relations[extentity.extid] = ext_dump_relations(cnx, extid2eid, extentity)
                # 2. remove the external uri entity
                cnx.execute('DELETE ExternalUri X WHERE X eid %(x)s', {'x': eid})
                # 3. drop its extid from the mapping to trigger insertion of the concept by the
                # importer
                del extid2eid[extentity.extid]
                # 4. will be done in SKOSExtEntitiesImporter
        return extentity

    entities = imap(externaluri_to_concept, entities)
    # plug function to detect the concept scheme
    concept_schemes = []

    def record_scheme(extentity):
        if extentity.etype == 'ConceptScheme':
            concept_schemes.append(extentity.extid)
        return extentity

    entities = imap(record_scheme, entities)
    etypes_order_hint = ('ConceptScheme', 'Concept', 'Label')
    existing_relations = SKOSRelationMapping(cnx, source)
    importer = SKOSExtEntitiesImporter(schema=cnx.vreg.schema, store=store,
                                       extid2eid=extid2eid, existing_relations=existing_relations,
                                       restore_relations=restore_relations,
                                       etypes_order_hint=etypes_order_hint, import_log=import_log,
                                       raise_on_error=raise_on_error)
    if extid_as_cwuri:
        set_cwuri = use_extid_as_cwuri(importer.extid2eid)
        entities = set_cwuri(entities)
    importer.import_entities(entities)
    stats = (importer.created, importer.updated)
    return stats, concept_schemes


class SKOSExtEntitiesImporter(ExtEntitiesImporter):
    """Override ExtEntitiesImporter to handle creation of additionnal relations to newly created
    concepts that replace a former external uri, and to create ExternalUri entities for URIs used in
    exact_match / close_match relations which have no known entity in the repository yet.
    """

    def __init__(self, *args, **kwargs):
        self.restore_relations = kwargs.pop('restore_relations')
        super(SKOSExtEntitiesImporter, self).__init__(*args, **kwargs)

    def prepare_insert_entity(self, extentity):
        eid = super(SKOSExtEntitiesImporter, self).prepare_insert_entity(extentity)
        # (4.) restore relations formerly from/to an equivalent external uri
        try:
            relations = self.restore_relations.pop(extentity.extid)
        except KeyError:
            return eid
        for subject_eid, rtype, object_eid in relations:
            if subject_eid is None:
                subject_eid = eid
            if object_eid is None:
                object_eid = eid
            self.store.prepare_insert_relation(subject_eid, rtype, object_eid)
        return eid

    def prepare_insert_deferred_relations(self, deferred):
        # create missing targets for exact_match and close_match relations
        for rtype in ('exact_match', 'close_match'):
            relations = deferred.get(rtype, ())
            for _, object_uri in relations:
                if object_uri not in self.extid2eid:
                    extentity = ExtEntity('ExternalUri', object_uri,
                                          values=dict(uri=text_type(object_uri),
                                                      cwuri=text_type(object_uri)))
                    self.prepare_insert_entity(extentity)
        return super(SKOSExtEntitiesImporter, self).prepare_insert_deferred_relations(deferred)
