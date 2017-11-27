#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: base.py
# Author: Jimin Huang <huangjimin@whu.edu.cn>
# Date: 27.10.2017
import arrow
import logging

from datetime import datetime, date, time
from decimal import Decimal
from sqlalchemy import BIGINT, Column
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declared_attr


LOGGER = logging.getLogger(__name__)

BASE_VALUE_TYPE = {
    datetime: "_datetime",
    time: "_time",
    date: "_date",
    Decimal: "_decimal"
}

TIME_FORMAT = '%H:%M:%S'
DATE_FORMAT = 'YYYY-MM-DD'
DATETIME_FORMAT = 'YYYY-MM-DD HH:mm:ss'


class DBBase(object):
    """Persisted object base class
    """
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column('id', BIGINT, primary_key=True)
    gmt_create = Column('gmt_create', DATETIME(fsp=6), default=func.now(6))
    gmt_modified = Column(
        'gmt_modified', DATETIME(fsp=6), default=func.now(6),
        onupdate=func.now(6)
    )

    @classmethod
    def add(cls, obj, session):
        """Add new obj with given session

        Args:
            obj: cls instance
            session: ``DBSession`` instance
        """
        session.add(obj)

    @classmethod
    def batch_add(cls, objs, session):
        """Batch add objects with given session

        Args:
            objs: a list of dicts
            session: ``DBSession`` instance
        """
        session.bulk_insert_mappings(cls, objs)

    @classmethod
    def delete_all(cls, session):
        """Delete all objects with given session

        Args:
            session: ``DBSession`` instance
        """
        session.query(cls).delete()

    @classmethod
    def query(cls, session):
        """Query all results

        Args:
            session: ``DBSession`` instance

        Return:
            a list of ``DBBase`` instances
        """
        return session.query(cls).all()

    def get_items(self):
        """Get columns and values from ``_sa_instance_state.attr.items()``
        """
        return self._sa_instance_state.attrs.items()

    def __repr__(self):
        """Return str format of the class

        Return:
            a str
        """
        return '{0}: {1}'.format(
            self.__class__.__name__,
            [(key, getattr(self, key)) for key, _ in self.get_items()]
        )

    def __eq__(self, other):
        """Overlap the eq method to compare object to dict.

        If key not in self, then return False, or get the value in self. If the
        type of the value in ``value_type_dict``, namely that the value need a
        transform before compare, call corresponding method in
        ``value_type_dict``. Finally, return if the value is equal to self
        value.

        Args:
            other: a dict with all key-value pairs to be compared.
        """
        if not isinstance(other, dict):
            LOGGER.info("Value not dict")
            return False

        for key, value in other.iteritems():
            try:
                self_value = getattr(self, key)
            except AttributeError:
                LOGGER.info("{0} not found in object".format(key))
                return False

            try:
                method = BASE_VALUE_TYPE[type(self_value)]
                self_value = getattr(self, method)(self_value)
            except KeyError:
                pass

            if self_value == value:
                continue
            LOGGER.info(
                "Value not matched for {0}: {1} | {2}".format(
                    key, self_value, value
                )
            )
            return False
        return True

    def _time(self, self_value):
        """Method to transform ``time``.

        Args:
            self_value: ``time`` instance

        Return:
            a str
        """
        return self_value.strftime(TIME_FORMAT)

    def _date(self, self_value):
        """Method to transform ``date``.

        Args:
            self_value: ``date`` instance

        Return:
            a str
        """
        return arrow.get(self_value).format(DATE_FORMAT)

    def _datetime(self, self_value):
        """Method to transform ``datetime``.

        Args:
            self_value: ``datetime`` instance

        Return:
            a str
        """
        return arrow.get(self_value).format(DATETIME_FORMAT)

    def _decimal(self, decimal):
        """Method to transform ``decimal.Decimal()``

        Args:
            self_value: ``Decimal`` instance

        Return:
            a str
        """
        return '{0:.3f}'.format(decimal)
