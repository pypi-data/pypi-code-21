# -*- coding: utf-8 -*-
"""
    baka_tenshi - schema
    ~~~~~~~~~~~~~~~~

    Adds basic SQLAlchemy support to your application.

    :copyright: (c) 2017 by Nanang Suryadi.
    :license: BSD, see LICENSE for more details.
"""
import time
from datetime import datetime, date

import sqlalchemy as sa
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import functions
from sqlalchemy.types import DateTime


class References(object):
    """A mixin which creates foreign key references to related classes."""
    _to_ref = set()
    _references = _to_ref.add

    @classmethod
    def __declare_first__(cls):
        """declarative hook called within the 'before_configure' mapper event."""
        for lcl, rmt in cls._to_ref:
            cls._decl_class_registry[lcl]._reference_table(
                cls._decl_class_registry[rmt].__table__)
        cls._to_ref.clear()

    @classmethod
    def _reference_table(cls, ref_table):
        """Create a foreign key reference from the local class to the given remote
        table.

        Adds column references to the declarative class and adds a
        ForeignKeyConstraint.

        """
        # create pairs of (Foreign key column, primary key column)
        cols = [(sa.Column(), refcol) for refcol in ref_table.primary_key]

        # set "tablename_colname = Foreign key Column" on the local class
        for col, refcol in cols:
            setattr(cls, "%s_%s" % (ref_table.name, refcol.name), col)

        # add a ForeignKeyConstraint([local columns], [remote columns])
        cls.__table__.append_constraint(sa.ForeignKeyConstraint(*zip(*cols)))


class JsonSerializableMixin(object):
    """
    Converts all the properties of the object into a dict for use in json.
    You can define the following as your class properties.

    _json_eager_load :
        list of which child classes need to be eagerly loaded. This applies
        to one-to-many relationships defined in SQLAlchemy classes.

    _base_blacklist :
        top level blacklist list of which properties not to include in JSON

    _json_blacklist :
        blacklist list of which properties not to include in JSON
    """

    def __json__(self, request):
        """
        Main JSONify method

        :param request: Pyramid Request object
        :type request: <Request>
        :return: dictionary ready to be jsonified
        :rtype: <dict>
        """

        props = {}

        # grab the json_eager_load set, if it exists
        # use set for easy 'in' lookups
        json_eager_load = set(getattr(self, '_json_eager_load', []))
        # now load the property if it exists
        # (does this issue too many SQL statements?)
        for prop in json_eager_load:
            getattr(self, prop, None)

        # we make a copy because the dict will change if the database
        # is updated / flushed
        options = self.__dict__.copy()

        # setup the blacklist
        # use set for easy 'in' lookups
        blacklist = set(getattr(self, '_base_blacklist', []))
        # extend the base blacklist with the json blacklist
        blacklist.update(getattr(self, '_json_blacklist', []))

        for key in options:
            # skip blacklisted properties
            if key in blacklist:
                continue
            # do not include private and SQLAlchemy properties
            if key.startswith(('__', '_sa_')):
                continue

            # format and date/datetime/time properties to isoformat
            obj = getattr(self, key)
            if isinstance(obj, (datetime, date, time)):
                props[key] = obj.isoformat()
                continue

            # get the class property value
            attr = getattr(self, key)
            # let see if we need to eagerly load it
            # this is for SQLAlchemy foreign key fields that
            # indicate with one-to-many relationships
            if key in json_eager_load and attr:
                if hasattr(attr, '_sa_instance_state'):
                    props[key] = self.__try_to_json(request, attr)
                else:
                    # jsonify all child objects
                    props[key] = [self.__try_to_json(request, x) for x in attr]
                continue

            # convert all non integer strings to string or if string conversion
            # is not possible, convert it to Unicode
            if attr and not isinstance(attr, (int, float)):
                try:
                    props[key] = str(attr)
                except UnicodeEncodeError:
                    props[key] = unicode(attr)  # .encode('utf-8')
                continue

            props[key] = attr

        return props

    def __try_to_json(self, request, attr):
        """
        Try to run __json__ on the given object.
        Raise TypeError is __json__ is missing

        :param request: Pyramid Request object
        :type request: <Request>
        :param obj: Object to JSONify
        :type obj: any object that has __json__ method
        :exception: TypeError
        """

        # check for __json__ method and try to JSONify
        if hasattr(attr, '__json__'):
            return attr.__json__(request)

        # raise error otherwise
        raise TypeError('__json__ method missing on %s' % str(attr))


class utcnow(functions.FunctionElement):
    key = 'utcnow'
    type = DateTime()


@compiles(utcnow)
def _default_utcnow(element, compiler, **kw):
    """default compilation handler.

    Note that there is no SQL "utcnow()" function; this is a
    "fake" string so that we can produce SQL strings that are dialect-agnostic,
    such as within tests.

    """
    return "utcnow()"


@compiles(utcnow, 'mysql')
def _sqlite_utcnow(element, compiler, **kw):
    """Mysql-specific compilation handler."""
    return "UTC_TIMESTAMP()"


@compiles(utcnow, 'sqlite')
def _sqlite_utcnow(element, compiler, **kw):
    """SQLite-specific compilation handler."""
    return "CURRENT_TIMESTAMP"


@compiles(utcnow, 'postgresql')
def _pg_utcnow(element, compiler, **kw):
    """Postgresql-specific compilation handler."""

    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


@sa.event.listens_for(sa.Table, "after_parent_attach")
def timestamp_cols(table, metadata):
    from .meta import Base

    if metadata is Base.metadata:
        table.append_column(
            sa.Column('created',
                      sa.DateTime(),
                      nullable=False,
                      server_default=sa.func.now(),
                      default=utcnow())
        )
        table.append_column(
            sa.Column('modified',
                      sa.DateTime(),
                      nullable=False,
                      server_default=sa.func.now(),
                      default=utcnow(),
                      onupdate=utcnow())
        )
