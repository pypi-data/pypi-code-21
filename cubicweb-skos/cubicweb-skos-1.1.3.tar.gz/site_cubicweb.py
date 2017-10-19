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
"""cubicweb-skos site customizations"""

# pylint: disable=wrong-import-order

from datetime import datetime

from six import text_type

from logilab.common.decorators import monkeypatch

from cubes.skos import POST_321, POST_323

if not POST_321:
    from copy import copy
    import inspect

    from cubicweb.dataimport import MetaGenerator, NoHookRQLObjectStore

    @monkeypatch(MetaGenerator)
    def __init__(self, cnx, baseurl=None, source=None):
        self._cnx = cnx
        if baseurl is None:
            config = cnx.vreg.config
            baseurl = config['base-url'] or config.default_base_url()
        if not baseurl[-1] == '/':
            baseurl += '/'
        self.baseurl = baseurl
        if source is None:
            source = cnx.repo.system_source
        self.source = source
        self.create_eid = cnx.repo.system_source.create_eid
        self.time = datetime.now()
        # attributes/relations shared by all entities of the same type
        self.etype_attrs = []
        self.etype_rels = []
        # attributes/relations specific to each entity
        self.entity_attrs = ['cwuri']
        schema = cnx.vreg.schema
        rschema = schema.rschema
        for rtype in self.META_RELATIONS:
            # skip owned_by / created_by if user is the internal manager
            if cnx.user.eid == -1 and rtype in ('owned_by', 'created_by'):
                continue
            if rschema(rtype).final:
                self.etype_attrs.append(rtype)
            else:
                self.etype_rels.append(rtype)

    @monkeypatch(MetaGenerator)
    def init_entity(self, entity):
        entity.eid = self.create_eid(self._cnx)
        extid = entity.cw_edited.get('cwuri')
        for attr in self.entity_attrs:
            if attr in entity.cw_edited:
                # already set, skip this attribute
                continue
            genfunc = self.generate(attr)
            if genfunc:
                entity.cw_edited.edited_attribute(attr, genfunc(entity))
        if isinstance(extid, text_type):
            extid = extid.encode('utf-8')
        return self.source, extid

    @monkeypatch(NoHookRQLObjectStore)
    def create_entity(self, etype, **kwargs):
        for key, value in kwargs.iteritems():
            kwargs[key] = getattr(value, 'eid', value)
        entity, rels = self.metagen.base_etype_dicts(etype)
        # make a copy to keep cached entity pristine
        entity = copy(entity)
        entity.cw_edited = copy(entity.cw_edited)
        entity.cw_clear_relation_cache()
        entity.cw_edited.update(kwargs, skipsec=False)
        entity_source, extid = self.metagen.init_entity(entity)
        cnx = self._cnx
        self.source.add_info(cnx, entity, entity_source, extid)
        self.source.add_entity(cnx, entity)
        kwargs = dict()
        if inspect.getargspec(self.add_relation).keywords:
            kwargs['subjtype'] = entity.cw_etype
        for rtype, targeteids in rels.iteritems():
            # targeteids may be a single eid or a list of eids
            inlined = self.rschema(rtype).inlined
            try:
                for targeteid in targeteids:
                    self.add_relation(cnx, entity.eid, rtype, targeteid,
                                      inlined, **kwargs)
            except TypeError:
                self.add_relation(cnx, entity.eid, rtype, targeteids,
                                  inlined, **kwargs)
        self._nb_inserted_entities += 1
        return entity


if not POST_323:
    # asynchronous source synchronization from the UI (https://www.cubicweb.org/ticket/10468967)
    # other part in views/__init__.py

    from pytz import utc
    from cubicweb import ObjectNotFound
    from cubicweb.server.sources import datafeed

    @monkeypatch(datafeed.DataFeedSource)
    def pull_data(self, cnx, force=False, raise_on_error=False, import_log_eid=None):
        """Launch synchronization of the source if needed.

        This method is responsible to handle commit/rollback on the given
        connection.
        """
        if not force and self.fresh():
            return {}
        if not self.acquire_synchronization_lock(cnx, force):
            return {}
        try:
            return self._pull_data(cnx, force, raise_on_error, import_log_eid)
        finally:
            cnx.rollback()  # rollback first in case there is some dirty transaction remaining
            self.release_synchronization_lock(cnx)

    @monkeypatch(datafeed.DataFeedSource)
    def _pull_data(self, cnx, force=False, raise_on_error=False, import_log_eid=None):
        importlog = self.init_import_log(cnx, import_log_eid)
        myuris = self.source_cwuris(cnx)
        try:
            parser = self._get_parser(cnx, sourceuris=myuris, import_log=importlog)
        except ObjectNotFound:
            return {}
        if self.process_urls(parser, self.urls, raise_on_error):
            self.warning("some error occurred, don't attempt to delete entities")
        else:
            parser.handle_deletion(self.config, cnx, myuris)
        self.update_latest_retrieval(cnx)
        stats = parser.stats
        if stats.get('created'):
            importlog.record_info('added %s entities' % len(stats['created']))
        if stats.get('updated'):
            importlog.record_info('updated %s entities' % len(stats['updated']))
        importlog.write_log(cnx, end_timestamp=self.latest_retrieval)
        cnx.commit()
        return stats

    @monkeypatch(datafeed.DataFeedSource)
    def init_import_log(self, cnx, import_log_eid=None, **kwargs):
        if import_log_eid is None:
            import_log = cnx.create_entity('CWDataImport', cw_import_of=self,
                                           start_timestamp=datetime.now(tz=utc),
                                           **kwargs)
        else:
            import_log = cnx.entity_from_eid(import_log_eid)
            import_log.cw_set(start_timestamp=datetime.now(tz=utc), **kwargs)
        cnx.commit()
        import_log.init()
        return import_log

    @monkeypatch(datafeed.DataFeedSource)
    def acquire_synchronization_lock(self, cnx, force=False):
        # XXX race condition until WHERE of SET queries is executed using
        # 'SELECT FOR UPDATE'
        now = datetime.now(tz=utc)
        if force:
            maxdt = now
        else:
            maxdt = now - self.max_lock_lifetime
        if not cnx.execute(
                'SET X in_synchronization %(now)s WHERE X eid %(x)s, '
                'X in_synchronization NULL OR X in_synchronization < %(maxdt)s',
                {'x': self.eid, 'now': now, 'maxdt': maxdt}):
            self.error('concurrent synchronization detected, skip pull')
            cnx.commit()
            return False
        cnx.commit()
        return True
