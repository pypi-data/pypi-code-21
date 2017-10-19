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
"""SKOS Import code specific to cubicweb < 3.21"""

from itertools import imap

from six import text_type

from cubes.skos import ExtEntity
from cubes.skos.dataimport import ExtEntitiesImporter, cwuri2eid
from cubes.skos.dataimport import HTMLImportLog  # noqa

from cubes.skos.sobjects import ext_dump_relations


def store_skos_extentities(cnx, store, entities, import_log,
                           source=None, raise_on_error=False, extid_as_cwuri=True):
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
    * `extid_as_cwuri`, boolean flag telling if we should use the external entities'extid as
      `cwuri` attribute of imported entities (default to `True`)
    """
    # only consider the system source for schemes and labels
    if source is None:
        source_eid = cnx.repo.system_source.eid
    else:
        source_eid = source.eid
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
    importer = SKOSExtEntitiesImporter(cnx, store, import_log, source=source, extid2eid=extid2eid,
                                       raise_on_error=raise_on_error,
                                       etypes_order_hint=etypes_order_hint,
                                       restore_relations=restore_relations)
    stats = importer.import_entities(entities, use_extid_as_cwuri=extid_as_cwuri)
    return stats, concept_schemes


class SKOSExtEntitiesImporter(ExtEntitiesImporter):
    """Override ExtEntitiesImporter to handle creation of additionnal relations to newly created
    concepts that replace a former external uri, and to create ExternalUri entities for URIs used in
    exact_match / close_match relations which have no known entity in the repository yet.
    """

    def __init__(self, *args, **kwargs):
        self.restore_relations = kwargs.pop('restore_relations')
        super(SKOSExtEntitiesImporter, self).__init__(*args, **kwargs)

    def create_entity(self, extentity):
        entity = super(SKOSExtEntitiesImporter, self).create_entity(extentity)
        # (4.) restore relations formerly from/to an equivalent external uri
        try:
            relations = self.restore_relations.pop(extentity.extid)
        except KeyError:
            return entity
        for subject_eid, rtype, object_eid in relations:
            if subject_eid is None:
                subject_eid = entity.eid
            if object_eid is None:
                object_eid = entity.eid
            self.store.relate(subject_eid, rtype, object_eid)
        return entity

    def create_deferred_relations(self, deferred):
        # create missing targets for exact_match and close_match relations
        for rtype in ('exact_match', 'close_match'):
            relations = deferred.get(rtype, ())
            for _, object_uri in relations:
                if object_uri not in self.extid2eid:
                    extentity = ExtEntity('ExternalUri', object_uri,
                                          values=dict(uri=text_type(object_uri),
                                                      cwuri=text_type(object_uri)))
                    assert self.create_entity(extentity).cw_etype == 'ExternalUri'
        return super(SKOSExtEntitiesImporter, self).create_deferred_relations(deferred)

    def existing_relations(self, rtype):
        """return a set of (subject, object) eids already related by `rtype`"""
        if rtype in ('exact_match', 'close_match'):
            rql = 'Any X,O WHERE X %s O' % rtype
            return set(tuple(x) for x in self.cnx.execute(rql))
        return super(SKOSExtEntitiesImporter, self).existing_relations(rtype)
