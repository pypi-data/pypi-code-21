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

import logging
from itertools import imap

from six import text_type

from logilab.mtconverter import xml_escape


def cwuri2eid(cnx, etypes, source_eid=None):
    """return a dictionary mapping cwuri to eid for already imported entities"""
    rql = 'Any U, X WHERE X cwuri U'
    args = {}
    if len(etypes) == 1:
        rql += ', X is %s' % etypes[0]
    else:
        assert etypes, 'no entity types specified'
        rql += ', X is IN (%s)' % ','.join(etypes)
    if source_eid is not None:
        rql += ', X cw_source S, S eid %(s)s'
        args['s'] = source_eid
    return dict(cnx.execute(rql, args))


class ExtEntitiesImporter(object):
    """This class is responsible for importing a transitional representation
    of entities coming from an external source. These external entities are
    expected to be instances of `ExtEntity` built from the entity type, the
    extid (as a string) and a dict mapping attributes and subject relations to
    the set of corresponding values.

    ::

        ExtEntity(etype='Label',
                  extid='http://example.org/ark:/000000/123',
                  values={'label': set([u'toto']),
                          'pref_label_of': set(['http://example.org/ark:/000000/456']),
                         }
                 )
    """

    def __init__(self, cnx, store, import_log, source=None,
                 raise_on_error=False, etypes_order_hint=(), extid2eid=None):
        self.cnx = cnx
        self.store = store
        self.import_log = import_log
        if source is None:
            source = self.cnx.repo.system_source
        self.source = source
        self.raise_on_error = raise_on_error
        self.etypes_order_hint = etypes_order_hint
        # index of already imported entities
        if extid2eid is None:
            extid2eid = cwuri2eid(cnx, etypes_order_hint, source.eid)
        self.extid2eid = extid2eid
        self.updated = None
        self.created = None

    def import_entities(self, entities, use_extid_as_cwuri=True, skip_known_external_uris=True):
        """Import external entities given as ``ExtEntity``s.

        Parameters:

        * `use_extid_as_cwuri` use external entity's extid as cwuri (True by default).

        * `skip_known_external_uris` skip ExternalUri entities which are already known (True by
          default).

        """
        if use_extid_as_cwuri:
            def set_cwuri_if_needed(extentity, extid2eid=self.extid2eid):
                """Use external entity's extid as cwuri"""
                if extentity.extid not in extid2eid:
                    extentity.values['cwuri'] = set([text_type(extentity.extid)])
                return extentity
            entities = imap(set_cwuri_if_needed, entities)
        if skip_known_external_uris:
            entities = (ee for ee in entities
                        if not (ee.etype == 'ExternalUri' and ee.extid in self.extid2eid))
        # {etype: [etype dict]} of entities that are in the import queue
        queue = {}
        # set of created/updated eids
        self.created = set()
        self.updated = set()
        # order entity dictionaries then create/update them
        deferred = self._import_entities(entities, queue)
        # create deferred relations that don't exist already
        missing_relations = self.create_deferred_relations(deferred)
        self._warn_about_missing_work(queue, missing_relations)
        return self.created, self.updated

    def _import_entities(self, entities, queue):
        entity_from_eid = self.cnx.entity_from_eid
        extid2eid = self.extid2eid
        deferred = {}  # non inlined relations that may be deferred
        self.import_log.record_debug('importing entities')
        for extentity in self.iter_ext_entities(entities, deferred, queue):
            try:
                entity = entity_from_eid(extid2eid[extentity.extid], extentity.etype)
                assert extentity.etype == entity.cw_etype
            except KeyError:
                self.create_entity(extentity)
            else:
                if extentity.values:
                    # XXX some inlined relations may already exists
                    entity.cw_set(**extentity.values)
                    self.updated.add(entity.eid)
        return deferred

    def create_entity(self, extentity):
        entity = self.store.create_entity(extentity.etype, **extentity.values)
        self.extid2eid[extentity.extid] = entity.eid
        self.created.add(entity.eid)
        return entity

    def create_deferred_relations(self, deferred):
        relate = self.store.relate
        rschema = self.cnx.vreg.schema.rschema
        extid2eid = self.extid2eid
        missing_relations = []
        for rtype, relations in deferred.items():
            self.import_log.record_debug('importing %s %s relations' % (len(relations), rtype))
            symmetric = rschema(rtype).symmetric
            existing = self.existing_relations(rtype)
            for subject_uri, object_uri in relations:
                try:
                    subject_eid = extid2eid[subject_uri]
                    object_eid = extid2eid[object_uri]
                except KeyError:
                    missing_relations.append((subject_uri, rtype, object_uri))
                    continue
                if (subject_eid, object_eid) not in existing:
                    relate(subject_eid, rtype, object_eid)
                    existing.add((subject_eid, object_eid))
                    if symmetric:
                        existing.add((object_eid, subject_eid))
        return missing_relations

    def _warn_about_missing_work(self, queue, missing_relations):
        error = self.import_log.record_error
        if queue:
            msgs = ["can't create some entities, is there some cycle or "
                    "missing data?"]
            for ext_entities in queue.values():
                for extentity in ext_entities:
                    msgs.append(str(extentity))
            map(error, msgs)
            if self.raise_on_error:
                raise Exception('\n'.join(msgs))
        if missing_relations:
            msgs = ["can't create some relations, is there missing data?"]
            for subject_uri, rtype, object_uri in missing_relations:
                msgs.append("%s %s %s" % (subject_uri, rtype, object_uri))
            map(error, msgs)
            if self.raise_on_error:
                raise Exception('\n'.join(msgs))

    def existing_relations(self, rtype):
        """return a set of (subject, object) eids already related by `rtype`"""
        rql = 'Any X,O WHERE X %s O, X cw_source S, O cw_source S, S eid %%(s)s' % rtype
        return set(tuple(x) for x in self.cnx.execute(rql, {'s': self.source.eid}))

    def iter_ext_entities(self, entities, deferred, queue):
        """Yield external entities in an order which attempts to satisfy
        schema constraints (inlined / cardinality) and to optimize the import.
        """
        schema = self.cnx.vreg.schema
        extid2eid = self.extid2eid
        for extentity in entities:
            # check data in the transitional representation and prepare it for
            # later insertion in the database
            for subject_uri, rtype, object_uri in extentity.prepare(schema):
                deferred.setdefault(rtype, set()).add((subject_uri, object_uri))
            if not extentity.is_ready(extid2eid):
                queue.setdefault(extentity.etype, []).append(extentity)
                continue
            yield extentity
            # check for some entities in the que that may now be ready
            for etype in self.etypes_order_hint:
                if etype in queue:
                    new_queue = []
                    for extentity in queue[etype]:
                        if extentity.is_ready(extid2eid):
                            yield extentity
                        else:
                            new_queue.append(extentity)
                    if new_queue:
                        queue[etype][:] = new_queue
                    else:
                        del queue[etype]


class SimpleImportLog(object):
    """Fake CWDataImport log using a simple text format.

    Useful to display logs in the UI instead of storing them to the
    database.
    """

    def __init__(self, filename):
        self.logs = []
        self.filename = filename

    def record_debug(self, msg, path=None, line=None):
        self._log(logging.DEBUG, msg, path, line)

    def record_info(self, msg, path=None, line=None):
        self._log(logging.INFO, msg, path, line)

    def record_warning(self, msg, path=None, line=None):
        self._log(logging.WARNING, msg, path, line)

    def record_error(self, msg, path=None, line=None):
        self._log(logging.ERROR, msg, path, line)

    def record_fatal(self, msg, path=None, line=None):
        self._log(logging.FATAL, msg, path, line)

    def _log(self, severity, msg, path, line):
        encodedmsg = u'%s\t%s\t%s\t%s' % (severity, self.filename,
                                          line or u'', msg)
        self.logs.append(encodedmsg)


class HTMLImportLog(SimpleImportLog):
    """Fake CWDataImport log using a simple HTML format."""

    def _log(self, severity, msg, path, line):
        encodedmsg = u'%s\t%s\t%s\t%s<br/>' % (severity, self.filename,
                                               line or u'', xml_escape(msg))
        self.logs.append(encodedmsg)
