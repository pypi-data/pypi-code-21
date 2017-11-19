import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import TypeDecorator, CHAR


class MetaBase(object):
    """A meta base class for declarative base.

    Example usage:

        isinstance(SomeSQLAClass, MetaBase):
            ...

    """


def db_method(func):
    """Decorator for a database method of a `DataRepository` object.

    The decorated method's object must have its database session
    stored in self._dbsession`.

    """
    def wrapped_commit_func(self, *args, **kwargs):
        # Determine if we'll issue a commit or not. Remove 'commit'
        # from kwargs anyway.
        commit = kwargs.pop('commit', True)
        if getattr(self._dbsession, '_ya_in_transaction', False):
            commit = False

        retval = func(self, *args, **kwargs)

        if commit:
            self._dbsession.commit()

        return retval

    return wrapped_commit_func


class GUIDType(TypeDecorator):
    """Platform-independent GUID type.

    Uses Postgresql's UUID type, otherwise uses CHAR(32), storing as
    stringified hex values.

    Inspired from: http://docs.sqlalchemy.org/en/rel_0_8/core/types.html

    """

    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is not None:
            return uuid.UUID(value)
        return None
