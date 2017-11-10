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
Data Batch Handlers
"""

from __future__ import unicode_literals, absolute_import

import os
import shutil
import warnings

from sqlalchemy import orm

from rattail.db.cache import cache_model
from rattail.util import progress_loop, load_object


class BatchHandler(object):
    """
    Base class and partial default implementation for batch handlers.  It is
    expected that all batch handlers will ultimately inherit from this base
    class, therefore it defines the implementation "interface" loosely
    speaking.  Custom batch handlers are welcome to supplement or override this
    as needed, and in fact must do so for certain aspects.

    .. attribute: populate_batches

       Simple flag to indicate whether any/all batches being handled, will
       require initial population from a relevant data source.  Note that this
       flag should be set to ``True`` if *any* batches may need population.
       Whether or not a given batch actually needs to be populated, is
       ultimately determined by the :meth:`should_populate()` method.
    """
    populate_batches = False

    def __init__(self, config):
        self.config = config
        self.enum = config.get_enum()

    @property
    def batch_model_class(self):
        """
        Reference to the data model class of the batch type for which this
        handler is responsible, e.g. :class:`rattail.db.model.LabelBatch`.
        Each handler must define this (or inherit from one that does).
        """
        raise NotImplementedError("You must set the 'batch_model_class' attribute "
                                  "for class '{}'".format(self.__class__.__name__))

    @property
    def batch_key(self):
        """
        The "batch type key" for the handler, e.g. ``'labels'``.  This isn't
        necessarily unique among handlers, but instead refers to a unique key
        for the type of batch being handled.  The handler needn't define this,
        as it is borrowed from :attr:`batch_model_class`.
        """
        return self.batch_model_class.batch_key

    def get_model_title(self):
        return self.batch_model_class.get_model_title()

    def make_basic_batch(self, session, progress=None, **kwargs):
        """
        Make a new "basic" batch, with no customization beyond what is provided
        by ``kwargs``, which are passed directly to the batch class constructor.
        """
        kwargs.setdefault('rowcount', 0)
        kwargs.setdefault('complete', False)
        batch = self.batch_model_class(**kwargs)
        session.add(batch)
        session.flush()
        return batch

    def make_batch(self, session, progress=None, **kwargs):
        """
        Make a new batch, with initial rows if applicable.
        """
        batch = self.make_basic_batch(session, progress=progress, **kwargs)
        self.init_batch(batch, progress=progress, **kwargs)
        return batch

    def init_batch(self, batch, progress=None, **kwargs):
        """
        Initialize the batch in whatever way might make sense.  Whether this is
        required at all is up to the batch handler etc.
        """

    def add_row(self, batch, row):
        """
        (Try to) Add the given row to the given batch.  This assumes it is a
        *new* row, perhaps along with other assumptions?
        """
        session = orm.object_session(batch)
        with session.no_autoflush:
            batch.data_rows.append(row)
            self.refresh_row(row)
        if not row.removed:
            batch.rowcount += 1

    @property
    def root_datadir(self):
        """
        The absolute path of the root folder in which data for this particular
        type of batch is stored.  The structure of this path is as follows:

        .. code-block:: none

           /{root_batch_data_dir}/{batch_type_key}

        * ``{root_batch_data_dir}`` - Value of the 'batch.files' option in the
          [rattail] section of config file.
        * ``{batch_type_key}`` - Unique key for the type of batch it is.

        .. note::
           While it is likely that the data folder returned by this method
           already exists, this method does not guarantee it.
        """
        return self.config.batch_filedir(self.batch_key)

    def datadir(self, batch):
        """
        Returns the absolute path of the folder in which the batch's source
        data file(s) resides.  Note that the batch must already have been
        persisted to the database.  The structure of the path returned is as
        follows:

        .. code-block:: none

           /{root_datadir}/{uuid[:2]}/{uuid[2:]}

        * ``{root_datadir}`` - Value returned by :meth:`root_datadir()`.
        * ``{uuid[:2]}`` - First two characters of batch UUID.
        * ``{uuid[2:]}`` - All batch UUID characters *after* the first two.

        .. note::
           While it is likely that the data folder returned by this method
           already exists, this method does not guarantee any such thing.  It
           is typically assumed that the path will have been created by a
           previous call to :meth:`make_batch()` however.
        """
        return os.path.join(self.root_datadir, batch.uuid[:2], batch.uuid[2:])

    def make_datadir(self, batch):
        """
        Returns the data folder specific to the given batch, creating if necessary.
        """
        datadir = self.datadir(batch)
        os.makedirs(datadir)
        return datadir

    # TODO: remove default attr?
    def set_input_file(self, batch, path, attr='filename'):
        """
        Assign the data file found at ``path`` to the batch.  This overwrites
        the given attribute (``attr``) of the batch and places a copy of the
        data file in the batch's data folder.
        """
        datadir = self.make_datadir(batch)
        filename = os.path.basename(path)
        shutil.copyfile(path, os.path.join(datadir, filename))
        setattr(batch, attr, filename)

    def should_populate(self, batch):
        """
        Must return a boolean indicating whether the given batch should be
        populated from an initial data source, i.e. at time of batch creation.
        Override this method if you need to inspect the batch in order to
        determine whether the populate step is needed.  Default behavior is to
        simply return the value of :attr:`populate_batches`.
        """
        return self.populate_batches

    def setup_populate(self, batch, progress=None):
        """
        Perform any setup (caching etc.) necessary for populating a batch.
        """

    def teardown_populate(self, batch, progress=None):
        """
        Perform any teardown (cleanup etc.) necessary after populating a batch.
        """

    def populate(self, batch, progress=None):
        """
        Populate the batch with initial data rows.  It is assumed that the data
        source to be used will be known by inspecting various properties of the
        batch itself.
        """
        raise NotImplementedError("Please implement `{}.populate()` method".format(batch.__class__.__name__))

    def refreshable(self, batch):
        """
        This method should return a boolean indicating whether or not the
        handler supports a "refresh" operation for the batch, given its current
        condition.  The default simply returns ``True`` but you may override as
        needed.

        Note that this (currently) only affects the enabled/disabled state of
        the Refresh button within the Tailbone batch view.
        """
        return not bool(batch.executed)

    def progress_loop(self, *args, **kwargs):
        return progress_loop(*args, **kwargs)

    def setup_refresh(self, batch, progress=None):
        """
        Perform any setup (caching etc.) necessary for refreshing a batch.
        """

    def teardown_refresh(self, batch, progress=None):
        """
        Perform any teardown (cleanup etc.) necessary after refreshing a batch.
        """

    def refresh(self, batch, progress=None):
        """
        Perform a full data refresh for the batch.  What exactly this means will
        depend on the type of batch, and specific handler logic.

        Generally speaking this refresh is meant to use queries etc. to obtain
        "fresh" data for the batch (header) and all its rows.  In most cases
        certain data is expected to be "core" to the batch and/or rows, and
        such data will be left intact, with all *other* data values being
        re-calculated and/or reset etc.
        """
        session = orm.object_session(batch)
        self.setup_refresh(batch, progress=progress)
        batch.rowcount = 0

        def refresh(row, i):
            with session.no_autoflush:
                self.refresh_row(row)
            if not row.removed:
                batch.rowcount += 1

        success = self.progress_loop(refresh, batch.active_rows(), progress,
                                     message="Refreshing batch data rows")
        self.refresh_batch_status(batch)
        self.teardown_refresh(batch, progress=progress)
        return success

    def refresh_row(self, row):
        """
        This method will be passed a row object which has already been properly
        added to a batch, and which has basic required fields already
        populated.  This method is then responsible for further populating all
        applicable fields for the row, based on current data within the
        relevant system(s).

        Note that in some cases this method may be called multiple times for
        the same row, e.g. once when first creating the batch and then later
        when a user explicitly refreshes the batch.  The method logic must
        account for this possibility.
        """

    def refresh_batch_status(self, batch):
        """
        Update the batch status, as needed...
        """

    def executable(self, batch):
        """
        This method should return a boolean indicating whether or not execution
        should be allowed for the batch, given its current condition.  The
        default simply returns ``True`` but you may override as needed.

        Note that this (currently) only affects the enabled/disabled state of
        the Execute button within the Tailbone batch view.
        """
        if batch is None:
            return True
        return not bool(batch.executed)

    def execute(self, batch, progress=None, **kwargs):
        """
        Execute the given batch, with given progress and kwargs.  That is an
        intentionally generic statement, the meaning of which must be further
        defined by the handler subclass since default is ``NotImplementedError``.
        """
        raise NotImplementedError

    def execute_many(self, batches, progress=None, **kwargs):
        """
        Execute a set of batches, with given progress and kwargs.  That is an
        intentionally generic statement, the meaning of which must be further
        defined by the handler subclass since default is ``NotImplementedError``.
        """
        raise NotImplementedError

    def clone(self, oldbatch, created_by):
        """
        Clone the given batch as a new batch, and return the new batch.
        """
        newbatch = self.batch_model_class()
        newbatch.created_by = created_by
        rowclass = newbatch.row_class
        mapper = orm.class_mapper(rowclass)

        for oldrow in oldbatch.data_rows:
            newrow = rowclass()
            for name in mapper.columns.keys():
                if name not in ('uuid', 'batch_uuid'):
                    setattr(newrow, name, getattr(oldrow, name))
            newbatch.data_rows.append(newrow)

        session = orm.object_session(oldbatch)
        session.add(newbatch)
        session.flush()
        return newbatch

    def cache_model(self, session, model, **kwargs):
        return cache_model(session, model, **kwargs)


def get_batch_handler(config, batch_key, default=None):
    """
    Returns a batch handler object corresponding to the given batch key.
    """
    spec = config.get('rattail.batch', '{}.handler'.format(batch_key), default=default)
    assert spec, "no handler spec could be determined for batch type: {}".format(batch_key)
    handler = load_object(spec)(config)
    return handler
