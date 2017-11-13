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

"""cubicweb-datacat specific hooks and operations"""

import os
from datetime import datetime

from pytz import utc

from cubicweb.predicates import (
    has_related_entities,
    is_instance,
)
from cubicweb.server import hook
from cubicweb.server.sources import storages

from cubes.datacat import concept_in


class ServerStartupHook(hook.Hook):
    __regid__ = 'datacat.serverstartup'
    events = ('server_startup', 'server_maintenance')

    def __call__(self):
        bfssdir = os.path.join(self.repo.config.appdatahome, 'bfss')
        if not os.path.exists(bfssdir):
            os.makedirs(bfssdir)
            print 'created', bfssdir
        storage = storages.BytesFileSystemStorage(bfssdir)
        storages.set_attribute_storage(self.repo, 'File', 'data', storage)


class InitDatedEntityHook(hook.Hook):
    """Initialize issued/modified attributes of entities."""
    __regid__ = 'datacat.init-dates'
    __select__ = hook.Hook.__select__ & is_instance('DataCatalog', 'Dataset',
                                                    'Distribution')
    events = ('before_add_entity', )

    def __call__(self):
        now = datetime.now(utc)
        issued = self.entity.cw_edited.setdefault('issued', now)
        self.entity.cw_edited.setdefault('modified', issued)


class UpdateDatedEntityHook(hook.Hook):
    """Update "modified" attribute of entities."""
    __regid__ = 'datacat.update-modified'
    __select__ = hook.Hook.__select__ & is_instance('DataCatalog', 'Dataset',
                                                    'Distribution')
    events = ('before_update_entity', )

    def __call__(self):
        now = datetime.now(utc)
        self.entity.cw_edited.setdefault('modified', now)


class CreateDistributionForResourceFeedHook(hook.Hook):
    """Create a distribution associated with a ResourceFeed upon addition of
    `resource_feed_of` relation.
    """
    __regid__ = 'datacat.resourcefeed_distribution'
    __select__ = hook.Hook.__select__ & hook.match_rtype('resource_feed_of')
    events = ('after_add_relation', )

    def __call__(self):
        resourcefeed = self._cw.entity_from_eid(self.eidfrom)
        # We do not handle "update" of resource_feed_of relation, but this
        # should not occur in practice.
        assert not resourcefeed.resourcefeed_distribution, \
            'ResourceFeed already has a related distribution'
        dataset = self._cw.entity_from_eid(self.eidto)
        self._cw.create_entity('Distribution',
                               title=resourcefeed.title,
                               media_type=resourcefeed.media_type,
                               of_dataset=dataset,
                               reverse_resourcefeed_distribution=resourcefeed)


class UpdateDistributionModificationDateFromFileHook(hook.Hook):
    """Update the modification_date of the Distribution when related to a
    File.
    """
    __regid__ = 'datacat.update-distribution-modification-date-from-file'
    __select__ = hook.Hook.__select__ & has_related_entities('file_distribution')
    events = ('after_update_entity', )

    def __call__(self):
        # XXX spurious implementation, needs review.
        if self.entity.has_eid():
            dist = self.entity.file_distribution[0]
            dist.cw_set(modified=datetime.now(utc))


class DistributionMetadataFromFileHook(hook.Hook):
    """Set Distribution metadata according its related File."""
    __regid__ = 'datacat.set_distribution_metadata_from_file'
    __select__ = hook.Hook.__select__ & hook.match_rtype('file_distribution')
    events = ('after_add_relation', )

    def __call__(self):
        distr = self._cw.entity_from_eid(self.eidto)
        distr_file = self._cw.entity_from_eid(self.eidfrom)
        distr_file.cw_set(title=distr.title, description=distr.description)
        now = datetime.now(utc)
        media_type = concept_in(
            self._cw, label=distr_file.data_format,
            scheme_uri=u'http://www.iana.org/assignments/media-types/media-types.xml')
        distr.cw_set(byte_size=distr_file.size(),
                     media_type=media_type,
                     issued=now,
                     modified=now)


class LinkFeedResourceToDistribution(hook.Hook):
    """Add the `file_distribution` relation to files produced by a
    transformation script when the latter is attached to a ResourceFeed (which
    is in turns related to a Distribution).

    If the Distribution already had a file attached, simply set the `File
    replaces File` relation, which in turns will set the file_distribution as
    per 'datacat.replace-file-distribution' hook.
    """
    __regid__ = 'datacat.link-feedresource-to-distribution'
    __select__ = hook.Hook.__select__ & hook.match_rtype('produced_by')
    events = ('after_add_relation', )

    def __call__(self):
        rset = self._cw.execute(
            'Any D WHERE R resourcefeed_distribution D,'
            '            TP process_for_resourcefeed R,'
            '            TP eid %(eid)s',
            {'eid': self.eidto})
        assert rset  # schema
        distr_eid, newfile_eid = rset[0][0], self.eidfrom
        # Make old distribution file replaced by new file.
        rset = self._cw.execute(
            'SET NEWF replaces OLDF WHERE OLDF file_distribution D,'
            '                             D eid %(d)s, NEWF eid %(f)s',
            {'d': distr_eid, 'f': newfile_eid})
        if rset:
            self.info('added file #%d (produced by process #%d) as a new '
                      'version of distribution %#d',
                      newfile_eid, self.eidto, distr_eid)
        # Then relate produced file to distribution.
        self._cw.execute(
            'SET F file_distribution D WHERE D eid %(d)s, F eid %(f)s',
            {'d': distr_eid, 'f': newfile_eid})
        self.info('added file #%d (produced by process #%d) to distribution %#d',
                  newfile_eid, self.eidto, distr_eid)


class ClearReplacedFilesHook(hook.Hook):
    """Triggers deletion of replaced files according to versions_to_keep's
    ResourceFeed parameter.
    """
    __regid__ = 'datacat.clear-replaced-files'
    __select__ = hook.Hook.__select__ & hook.match_rtype('replaces')
    events = ('after_add_relation', )

    def __call__(self):
        ClearReplacedFilesOp.get_instance(self._cw).add_data(self.eidfrom)


class ClearReplacedFilesOp(hook.DataOperationMixIn, hook.Operation):

    def precommit_event(self):
        for eid in self.get_data():
            f = self.cnx.entity_from_eid(eid)
            assert f.file_distribution, (
                'file #%d is replacing another one but is not related to a '
                'distribution'.format(eid))
            distribution = f.file_distribution[0]
            assert distribution.reverse_resourcefeed_distribution, (
                'expecting distribution #%d to be related to a resource '
                'feed'.format(distribution.eid))
            resourcefeed = distribution.reverse_resourcefeed_distribution[0]
            # Walk replaced files until limit.
            for count in range(resourcefeed.versions_to_keep + 1):
                if not f.replaces:
                    # Number of files is below limit.
                    break
                f = f.replaces[0]
            else:
                self.info('deleting replaced File #%d', f.eid)
                f.cw_delete()


class AddCWSourceForResourceFeedHook(hook.Hook):
    """Add a CWSource for ResourceFeed entities."""
    __regid__ = 'datacat.add_cwsource_for_resourcefeed'
    __select__ = hook.Hook.__select__ & is_instance('ResourceFeed')
    events = ('after_add_entity', )

    def __call__(self):
        url = self.entity.cw_edited['url'].strip()
        name = u'{}-{}'.format(self.entity.eid, url.split('://')[-1])[:128]
        config = u'\n'.join([
            u'use-cwuri-as-url=no',
            u'synchronization-interval=7d',
        ])
        self._cw.create_entity(
            'CWSource', name=name, url=url, type=u'datafeed',
            config=config, parser=u'datacat.resourcefeed-parser',
            reverse_resource_feed_source=self.entity,
        )


class UpdateCWSourceForResourceFeedHook(hook.Hook):
    """Update ResourceFeed's CWSource when its url changes."""
    __regid__ = 'datacat.update_resourcefeed_cwsource'
    __select__ = hook.Hook.__select__ & is_instance('ResourceFeed')
    events = ('after_update_entity', )

    def __call__(self):
        if 'url' in self.entity.cw_edited:
            url = self.entity.cw_edited['url']
            source = self.entity.resource_feed_source[0]
            source.cw_set(url=url, name=url)


class AddTransformationSequenceHook(hook.Hook):
    """Add a TransformationSequence when a "transformation_script" relation is
    added.
    """
    __regid__ = 'datacat.add-transformation-sequence'
    __select__ = (hook.Hook.__select__
                  & hook.match_rtype('transformation_script'))
    events = ('after_add_relation', )

    def __call__(self):
        tseq = self._cw.create_entity('TransformationSequence')
        self._cw.create_entity('TransformationStep', index=0,
                               step_script=self.eidto, in_sequence=tseq)


class DropTransformationSequenceHook(hook.Hook):
    """Drop TransformationSequence when a "transformation_script" relation is
    deleted.
    """
    __regid__ = 'datacat.drop-transformation-sequence'
    __select__ = (hook.Hook.__select__
                  & hook.match_rtype('transformation_script'))
    events = ('before_delete_relation', )

    def __call__(self):
        tseq = self._cw.entity_from_eid(self.eidto).transformation_sequence
        tseq.cw_delete()
