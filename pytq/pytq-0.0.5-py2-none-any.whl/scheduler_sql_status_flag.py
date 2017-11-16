#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six
import sqlalchemy as sa
from datetime import datetime, timedelta
from .scheduler import StatusFlag
from .scheduler_sql import SqlScheduler


class SqlStatusFlagScheduler(SqlScheduler, StatusFlag):
    """
    Similar to :class:`~pytq.scheduler_sql.SqlScheduler`.

    New Feature:

    There's pre-defined integer - ``duplicate_flag``, will be stored in
    ``status`` column. there's a ``edit_at`` datetime column, represent the
    last time the row been edited.

    .. note::

        Any value greater or equal than ``duplicate_flag``, AND the ``edit_at``
        time is smaller ``update_interval`` seconds ago, means it is a duplicate
        item.

    :param duplicate_flag: int, represent a status code for finished / duplicate
    :param update_interval: int, represent need-to-update interval (unit: seconds)
    """

    def __init__(self, logger=None, uri=None, table=None,
                 duplicate_flag=None, update_interval=None):
        super(SqlStatusFlagScheduler, self). \
            __init__(logger=logger, uri=uri, table=table)
        self.pre_process_duplicate_flag_and_update_interval(
            duplicate_flag, update_interval,
        )

    def prepare_table(self):
        if isinstance(self.table, sa.Table):
            metadata = self.table.metadata
            metadata.create_all(self.engine)
        elif isinstance(self.table, six.string_types):
            metadata = sa.MetaData()
            table = sa.Table(
                self.table, metadata,
                sa.Column(self.id_key, sa.String(), primary_key=True),
                sa.Column(self.out_key, sa.PickleType()),
                sa.Column(self.status_key, sa.Integer()),
                sa.Column(self.edit_at_key, sa.DateTime())
            )
            metadata.create_all(self.engine)
            self.table = table

    @property
    def status_col(self):
        return getattr(self.table.c, self.status_key)

    @property
    def edit_at_col(self):
        return getattr(self.table.c, self.edit_at_key)

    def _default_is_duplicate(self, task):
        """
        Check the status flag is greater or equal than
        :attr:`~StatusFlagScheduler.duplicate_flag` and last edit time is with
        in recent :attr:`~StatusFlagScheduler.update_interval` seconds.
        """
        n_sec_ago = datetime.utcnow() - timedelta(seconds=self.update_interval)
        sql = sa.select(
            [sa.func.count(self.id_col), ]
        ).where(
            sa.and_(
                self.id_col == task.id,
                self.status_col >= self.duplicate_flag,
                self.edit_at_col >= n_sec_ago,
            )
        )
        row = self.connection.execute(sql).fetchone()
        if row[0] == 1:
            return True
        else:
            return False

    def _get_finished_id_set(self):
        """
        It's Primary key value set.
        """
        n_sec_ago = datetime.utcnow() - timedelta(seconds=self.update_interval)
        sql = sa.select([self.id_col]).\
            where(
                sa.and_(
                    self.status_col >= self.duplicate_flag,
                    self.edit_at_col >= n_sec_ago,
                )
        )
        cursor = self.connection.execute(sql)
        return set([row[0] for row in cursor])

    def _default_post_process(self, task):
        """
        Write serialized output_data to "_out" column.
        """
        ins = self.table.insert()
        row = {
            self.id_key: task.id,
            self.out_key: task.output_data,
            self.status_key: self.duplicate_flag,
            self.edit_at_key: datetime.utcnow(),
        }
        try:
            self.connection.execute(ins, row)
        except sa.exc.IntegrityError:
            row.pop(self.id_key)
            upd = self.table.update(). \
                where(self.id_col == task.id). \
                values(**row)
            self.connection.execute(upd)
