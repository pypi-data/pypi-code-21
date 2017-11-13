# copyright 2014-2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

"""cubicweb-datacat server objects"""

import hashlib

from cubicweb.predicates import match_user_groups
from cubicweb.server import Service
from cubicweb.server.sources import datafeed
from cubicweb.dataimport.stores import (
    MetadataGenerator,
    NoHookRQLObjectStore,
)
from cubicweb.dataimport.importer import (
    ExtEntitiesImporter,
    ExtEntity,
)


def compute_sha1hex(value):
    """Return the SHA1 hex digest of `value`."""
    return unicode(hashlib.sha1(value).hexdigest())


class ResourceFeedParser(datafeed.DataFeedParser):
    """Fetch files and apply validation and transformation processes before
    attaching them to their Dataset as Resources.
    """
    __regid__ = 'datacat.resourcefeed-parser'

    def resourcefeed(self):
        cwsource = self._cw.entity_from_eid(self.source.eid)
        if cwsource.reverse_resource_feed_source:
            return cwsource.reverse_resource_feed_source[0]

    def importer(self, url, extid2eid):
        """Return an ExtEntity importer."""
        cnx = self._cw
        schema = cnx.vreg.schema
        # XXX Using NoHookRQLObjectStore because RQLObjectStore does not
        # support setting cw_source relation.
        metagenerator = MetadataGenerator(cnx, source=self.source)
        store = NoHookRQLObjectStore(cnx, metagenerator)
        return ExtEntitiesImporter(schema, store, import_log=self.import_log,
                                   extid2eid=extid2eid)

    def extid2eid(self):
        qs = 'Any H,X WHERE X data_sha1hex H, X cw_source S, S eid %(s)s'
        args = {'s': self.source.eid}
        return dict(self._cw.execute(qs, args))

    def process(self, url, raise_on_error=False):
        """Build a File entity from data fetched from url"""
        resourcefeed = self.resourcefeed()
        if resourcefeed is None:
            self.error('parser "%s" cannot be used for a CWSource with a ResourceFeed attached',
                       self.__regid__)
            if raise_on_error:
                raise Exception('CWSource #%d has no ResourceFeed attached' % self.source.eid)
        stream = self.retrieve_url(url)
        data = stream.read()
        sha1hex = compute_sha1hex(data)
        self.import_log.record_info(
            'fetched data from {0} sha1={1}'.format(url, sha1hex))
        extid2eid = self.extid2eid()
        extentity = ExtEntity('File', sha1hex)
        if extentity.extid not in extid2eid:
            # Only set `values` when the entity does not already exist
            # (otherwise the importer will consider the entity for update
            # which is not what we want).
            extentity.values.update({
                'data_name': set([url.split('/')[-1]]),
                'data_sha1hex': set([sha1hex]),
                'data': set([data]),
                'cwuri': set([sha1hex]),
            })
        importer = self.importer(url, extid2eid)
        importer.import_entities([extentity])
        created, updated = importer.created, importer.updated
        msg, args = ('data import for %s completed: created %d entities, updated %s entities',
                     (url, len(created), len(updated)))
        self.info(msg, *args)
        self.import_log.record_info(msg % args)
        entity = None
        if created:
            assert not updated, 'unexpected update of entities {0}'.format(updated)
            assert len(created) == 1, created
            entity = self._cw.entity_from_eid(created.pop())
            self.stats['created'].add(entity.eid)
        if updated:
            assert not created, 'unexpected creation of entities {0}'.format(created)
            assert len(updated) == 1, updated
            entity = self._cw.entity_from_eid(updated.pop())
            self.stats['updated'].add(entity.eid)
        if entity is not None:
            # Ensure imported entity as a cw_source, otherwise re-import would
            # not work.
            assert entity.cw_source
            self.process_data(entity)

    def process_data(self, entity):
        """Launch validation and transformation scripts of all related
        ResourceFeed entities.
        """
        resourcefeed = self.resourcefeed()
        distribution = resourcefeed.resourcefeed_distribution[0]
        relations = {
            'data_format': resourcefeed.data_format,
            'file_distribution': distribution,
        }
        self.import_log.record_debug(
            'adding file #{0} to distribution #{1}'.format(
                entity.eid, distribution.eid))
        if distribution.reverse_file_distribution:
            distfile = distribution.reverse_file_distribution[0]
            self.import_log.record_debug(
                'file #{0} replaces previous distribution file #{1}'.format(
                    entity.eid, distfile.eid))
            relations['replaces'] = distfile
        entity.cw_set(**relations)

        # Launch validation/transformation processes.
        vprocess = None
        if resourcefeed.validation_script:
            vscript = resourcefeed.validation_script[0]
            vprocess = self._cw.create_entity('DataValidationProcess',
                                              process_for_resourcefeed=resourcefeed,
                                              validation_script=vscript,
                                              process_input_file=entity)
            msg, args = ('created validation process #%d for file #%d',
                         (vprocess.eid, entity.eid))
            self.info(msg, *args)
            self.import_log.record_info(msg % args)
        if resourcefeed.transformation_script:
            tseq = resourcefeed.transformation_script[0].transformation_sequence
            tprocess = self._cw.create_entity('DataTransformationProcess',
                                              process_for_resourcefeed=resourcefeed,
                                              transformation_sequence=tseq,
                                              process_input_file=entity,
                                              process_depends_on=vprocess)
            msg, args = ('created transformation process #%d for file #%d',
                         (tprocess.eid, entity.eid))
            self.info(msg, *args)
            self.import_log.record_info(msg % args)


def delete_process_logs_for(cnx, eid):
    """Delete old process log files for ResourceFeed with `eid`."""
    keep = cnx.entity_from_eid(eid).processes_to_keep
    process_etypes = cnx.vreg.schema['process_for_resourcefeed'].targets(
        'ResourceFeed', 'object')
    deleted = []
    for etype in process_etypes:
        rset = cnx.execute(
            'Any X ORDERBY X DESC LIMIT {limit}'
            ' WHERE X process_for_resourcefeed R, R eid %(eid)s,'
            ' X is {etype}'.format(etype=etype, limit=keep),
            {'eid': eid})
        if not rset:
            continue
        last_to_keep = rset[-1][0]
        qs = ('DELETE File F WHERE P process_stderr F, P is {etype}, P eid < {last},'
              ' P process_for_resourcefeed R, R eid %(eid)s').format(
                  etype=etype, last=last_to_keep)
        rset = cnx.execute(qs, {'eid': eid})
        deleted.extend([x for x, in rset])
    return deleted


class RemoveOldProcessesService(Service):
    __regid__ = 'datacat.clean-resourcefeed-process-logs'
    __select__ = match_user_groups('managers')

    def call(self, eid=None):
        def log_deleted(deleted, resourcefeed_eid):
            self.info('deleted process log files "%s" of ressource feed #%d',
                      ', '.join(map(str, deleted)), resourcefeed_eid)

        if eid is not None:
            deleted = delete_process_logs_for(self._cw, eid)
            log_deleted(deleted, eid)
        else:
            deleted = []
            for eid, in self._cw.find('ResourceFeed'):
                rf_deleted = delete_process_logs_for(self._cw, eid)
                log_deleted(rf_deleted, eid)
                deleted.extend(rf_deleted)
        return deleted
