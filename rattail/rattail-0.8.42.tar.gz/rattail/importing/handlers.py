# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Import Handlers
"""

from __future__ import unicode_literals, absolute_import

import sys
import logging

import six
import humanize

from rattail.time import make_utc
from rattail.util import OrderedDict
from rattail.mail import send_email


log = logging.getLogger(__name__)


class ImportHandler(object):
    """
    Base class for all import handlers.
    """
    host_title = None
    local_title = None
    progress = None
    dry_run = False
    commit_host_partial = False
    diff_max_display = 15

    def __init__(self, config=None, **kwargs):
        self.config = config
        self.enum = config.get_enum() if config else None
        self.importers = self.get_importers()
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def get_importers(self):
        """
        Returns a dict of all available importers, where the keys are model
        names and the values are importer factories.  All subclasses will want
        to override this.  Note that if you return an
        :class:`python:collections.OrderedDict` instance, you can affect the
        ordering of keys in the command line help system, etc.
        """
        return {}

    def get_importer_keys(self):
        """
        Returns the list of keys corresponding to the available importers.
        """
        return list(self.importers.iterkeys())

    def get_default_keys(self):
        """
        Returns the list of keys corresponding to the "default" importers.
        Override this if you wish certain importers to be excluded by default,
        e.g. when first testing them out etc.
        """
        return self.get_importer_keys()

    def get_importer(self, key, **kwargs):
        """
        Returns an importer instance corresponding to the given key.
        """
        if key in self.importers:
            kwargs.setdefault('handler', self)
            kwargs.setdefault('config', self.config)
            kwargs.setdefault('host_system_title', self.host_title)
            if hasattr(self, 'batch_size'):
                kwargs.setdefault('batch_size', self.batch_size)
            kwargs = self.get_importer_kwargs(key, **kwargs)
            return self.importers[key](**kwargs)

    def get_importer_kwargs(self, key, **kwargs):
        """
        Return a dict of kwargs to be used when construcing an importer with
        the given key.
        """
        return kwargs

    def import_data(self, *keys, **kwargs):
        """
        Import all data for the given importer/model keys.
        """
        self.import_began = make_utc(tzinfo=True)
        if 'dry_run' in kwargs:
            self.dry_run = kwargs['dry_run']
        self.progress = kwargs.pop('progress', getattr(self, 'progress', None))
        self.warnings = kwargs.get('warnings', False)
        kwargs.update({'dry_run': self.dry_run,
                       'progress': self.progress})

        self.setup()
        self.begin_transaction()
        changes = OrderedDict()

        try:
            for key in keys:
                importer = self.get_importer(key, **kwargs)
                if importer:
                    created, updated, deleted = importer.import_data()
                    changed = bool(created or updated or deleted)
                    logger = log.warning if changed and self.warnings else log.info
                    logger("{} -> {}: added {:,d}; updated {:,d}; deleted {:,d} {} records".format(
                        self.host_title, self.local_title, len(created), len(updated), len(deleted), key))
                    if changed:
                        changes[key] = created, updated, deleted
                else:
                    log.warning("skipping unknown importer: {}".format(key))
        except:
            if self.commit_host_partial and not self.dry_run:
                log.warning("{host} -> {local}: committing partial transaction on host {host} (despite error)".format(
                    host=self.host_title, local=self.local_title))
                self.commit_host_transaction()
            raise
        else:
            if changes:
                self.process_changes(changes)
            if self.dry_run:
                self.rollback_transaction()
            else:
                self.commit_transaction()

        self.teardown()
        return changes

    def setup(self):
        """
        Perform any additional setup if/as necessary, prior to running the
        import task(s).
        """

    def teardown(self):
        """
        Perform any cleanup necessary, after running the import task(s).
        """

    def begin_transaction(self):
        self.begin_host_transaction()
        self.begin_local_transaction()

    def begin_host_transaction(self):
        pass

    def begin_local_transaction(self):
        pass

    def rollback_transaction(self):
        self.rollback_host_transaction()
        self.rollback_local_transaction()

    def rollback_host_transaction(self):
        pass

    def rollback_local_transaction(self):
        pass

    def commit_transaction(self):
        self.commit_host_transaction()
        self.commit_local_transaction()

    def commit_host_transaction(self):
        pass

    def commit_local_transaction(self):
        pass

    def process_changes(self, changes):
        """
        This method is called any time changes occur, regardless of whether the
        import is running in "warnings" mode.  Default implementation does
        nothing; override as needed.
        """
        # TODO: This whole thing needs a re-write...but for now, waiting until
        # the old importer has really gone away, so we can share its email
        # template instead of bothering with something more complicated.

        if not self.warnings:
            return

        now = make_utc(tzinfo=True)
        data = {
            'local_title': self.local_title,
            'host_title': self.host_title,
            'argv': sys.argv,
            'runtime': humanize.naturaldelta(now - self.import_began),
            'changes': changes,
            'dry_run': self.dry_run,
            'render_record': RecordRenderer(self.config),
            'max_display': self.diff_max_display,
        }

        command = getattr(self, 'command', None)
        if command:
            data['command'] = '{} {}'.format(command.parent.name, command.name)
        else:
            data['command'] = None

        if command:
            key = '{}_{}_updates'.format(command.parent.name, command.name)
            key = key.replace('-', '_')
        else:
            key = 'rattail_import_updates'

        send_email(self.config, key, fallback_key='rattail_import_updates', data=data)
        log.info("{} -> {}: warning email was sent".format(self.host_title, self.local_title))


class BulkImportHandler(ImportHandler):
    """
    Base class for bulk import handlers.
    """

    def import_data(self, *keys, **kwargs):
        """
        Import all data for the given importer/model keys.
        """
        # TODO: still need to refactor much of this so can share with parent class
        self.import_began = make_utc(tzinfo=True)
        if 'dry_run' in kwargs:
            self.dry_run = kwargs['dry_run']
        self.progress = kwargs.pop('progress', getattr(self, 'progress', None))
        self.warnings = kwargs.pop('warnings', False)
        kwargs.update({'dry_run': self.dry_run,
                       'progress': self.progress})
        self.setup()
        self.begin_transaction()
        changes = OrderedDict()

        try:
            for key in keys:
                importer = self.get_importer(key, **kwargs)
                if not importer:
                    log.warning("skipping unknown importer: {}".format(key))
                    continue

                created = importer.import_data()
                log.info("{} -> {}: added {}, updated 0, deleted 0 {} records".format(
                    self.host_title, self.local_title, created, key))
                if created:
                    changes[key] = created
        except:
            if self.commit_host_partial and not self.dry_run:
                log.warning("{host} -> {local}: committing partial transaction on host {host} (despite error)".format(
                    host=self.host_title, local=self.local_title))
                self.commit_host_transaction()
            raise
        else:
            if self.dry_run:
                self.rollback_transaction()
            else:
                self.commit_transaction()

        self.teardown()
        return changes


class FromSQLAlchemyHandler(ImportHandler):
    """
    Handler for imports for which the host data source is represented by a
    SQLAlchemy engine and ORM.
    """
    host_session = None

    def make_host_session(self):
        """
        Subclasses must override this to define the host database connection.
        """
        raise NotImplementedError

    def get_importer_kwargs(self, key, **kwargs):
        kwargs = super(FromSQLAlchemyHandler, self).get_importer_kwargs(key, **kwargs)
        kwargs.setdefault('host_session', self.host_session)
        return kwargs

    def begin_host_transaction(self):
        self.host_session = self.make_host_session()

    def rollback_host_transaction(self):
        self.host_session.rollback()
        self.host_session.close()
        self.host_session = None

    def commit_host_transaction(self):
        self.host_session.commit()
        self.host_session.close()
        self.host_session = None


class ToSQLAlchemyHandler(ImportHandler):
    """
    Handler for imports which target a SQLAlchemy ORM on the local side.
    """
    session = None

    def make_session(self):
        """
        Subclasses must override this to define the local database connection.
        """
        raise NotImplementedError

    def get_importer_kwargs(self, key, **kwargs):
        kwargs = super(ToSQLAlchemyHandler, self).get_importer_kwargs(key, **kwargs)
        kwargs.setdefault('session', self.session)
        return kwargs

    def begin_local_transaction(self):
        self.session = self.make_session()

    def rollback_local_transaction(self):
        self.session.rollback()
        self.session.close()
        self.session = None

    def commit_local_transaction(self):
        self.session.commit()
        self.session.close()
        self.session = None


# TODO: this is still pretty hacky, but needed to get it in here for now
class RecordRenderer(object):
    """
    Record renderer for email notifications sent from data import jobs.
    """

    def __init__(self, config):
        self.config = config

    def __call__(self, record):
        return self.render(record)

    def render(self, record):
        """
        Render the given record.
        """
        key = record.__class__.__name__.lower()
        renderer = getattr(self, 'render_{}'.format(key), None)
        if renderer:
            return renderer(record)

        label = self.get_label(record)
        url = self.get_url(record)
        if url:
            return '<a href="{}">{}</a>'.format(url, label)
        return label

    def get_label(self, record):
        key = record.__class__.__name__.lower()
        label = getattr(self, 'label_{}'.format(key), self.label)
        return label(record)

    def label(self, record):
        return six.text_type(record)

    def get_url(self, record):
        """
        Fetch / generate a URL for the given data record.  You should *not*
        override this method, but do :meth:`url()` instead.
        """
        key = record.__class__.__name__.lower()
        url = getattr(self, 'url_{}'.format(key), self.url)
        return url(record)

    def url(self, record):
        """
        Fetch / generate a URL for the given data record.
        """
        if hasattr(record, 'uuid'):
            url = self.config.get('tailbone', 'url')
            if url:
                url = url.rstrip('/')
                name = '{}s'.format(record.__class__.__name__.lower())
                if name == 'persons': # FIXME, obviously this is a hack
                    name = 'people'
                url = '{}/{}/{{uuid}}'.format(url, name)
                return url.format(uuid=record.uuid)
