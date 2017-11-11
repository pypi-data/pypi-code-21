import datetime
import uuid
import json

import bcrypt
from collections import Iterable
from sqlalchemy import Unicode, TypeDecorator, String, CHAR, VARCHAR, SmallInteger, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.mutable import Mutable


class Password(str):
    """Coerce a string to a bcrypt password.

    Rationale: for an easy string comparison,
    so we can say ``some_password == 'hello123'``

    .. seealso::

        https://pypi.python.org/pypi/bcrypt/

    """

    def __new__(cls, value, salt=None, crypt=True):
        if isinstance(value, Unicode):
            value = value.encode('utf-8')
        if crypt:
            value = bcrypt.hashpw(value, salt or bcrypt.gensalt(4))
        return str.__new__(cls, value)

    def __eq__(self, other):
        if not isinstance(other, Password):
            other = Password(other, self)
        return str.__eq__(self, other)

    def __ne__(self, other):
        return not self.__eq__(other)


class PasswordType(TypeDecorator):
    """Coerce strings to bcrypted Password objects for the database.
        """

    impl = String(128)

    def process_bind_param(self, value, dialect):
        return Password(value)

    def process_result_value(self, value, dialect):
        # already crypted, so don't crypt again
        return Password(value, value, False)

    def __repr__(self):
        return "PasswordType()"


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

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
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)



class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.
        e.g data = Column(MutableDict.as_mutable(JSONEncodedDict))
    """

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class MutableDict(Mutable, dict):
    @classmethod
    def coerce(cls, key, value):
        """Convert plain dictionaries to MutableDict."""

        if not isinstance(value, MutableDict):
            if isinstance(value, dict):
                return MutableDict(value)

            # this call will raise ValueError
            return Mutable.coerce(key, value)
        else:
            return value

    def __setitem__(self, key, value):
        """Detect dictionary set events and emit change events."""

        dict.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        """Detect dictionary del events and emit change events."""

        dict.__delitem__(self, key)
        self.changed()


class EnumInt(object):
    def __init__(self, value, values):
        self.value = value
        self._values = values

    @property
    def title(self):
        return self.value if self.value is None else self._values[self.value][1]

    @property
    def key(self):
        return self.value is not None and self._values[self.value][0]

    def __eq__(self, other):
        values = list(map(lambda x: x[0], self._values))
        return (other in values) and self.value == values.index(other)

    def __str__(self):
        return self.value if self.value is None else u"%s, %s" % (
            self.value, self._values[self.value][1]
        )

    def __repr__(self):
        return u"EnumInt(%s)" % self

    def serialize(self):
        return {'key': self.key, 'value': self.value, 'title': self.title}


class EnumIntType(TypeDecorator):

    impl = SmallInteger
    values = None

    def __init__(self, values=None):
        super(EnumIntType, self).__init__()
        assert values is None or isinstance(values, Iterable), \
            u'Values must be None or iterable'
        self.values = values

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        values = list(map(lambda x: x[0], self.values))
        return values.index(value)

    def process_result_value(self, value, dialect):
        return EnumInt(value, self.values)


"""
    source: https://github.com/spoqa/sqlalchemy-utc/
    untuk standart tipe timedate format UTC
"""


class UtcDateTime(TypeDecorator):
    """Almost equivalent to :class:`~sqlalchemy.types.DateTime` with
    ``timezone=True`` option, but it differs from that by:

    - Never silently take naive :class:`~datetime.datetime`, instead it
      always raise :exc:`ValueError` unless time zone aware value.
    - :class:`~datetime.datetime` value's :attr:`~datetime.datetime.tzinfo`
      is always converted to UTC.
    - Unlike SQLAlchemy's built-in :class:`~sqlalchemy.types.DateTime`,
      it never return naive :class:`~datetime.datetime`, but time zone
      aware value, even with SQLite or MySQL.

    """

    impl = DateTime(timezone=True)

    def process_bind_param(self, value, dialect):
        if value is not None:
            if not isinstance(value, datetime.datetime):
                raise TypeError('expected datetime.datetime, not ' +
                                repr(value))
            elif value.tzinfo is None:
                raise ValueError('naive datetime is disallowed')
            return value.astimezone(utc)

    def process_result_value(self, value, dialect):
        if value is not None and value.tzinfo is None:
            value = value.replace(tzinfo=utc)
        return value


class Utc(datetime.tzinfo):
    """
    source: https://github.com/spoqa/sqlalchemy-utc/
    untuk standart tipe timedate format UTC
    """
    zero = datetime.timedelta(0)

    def utcoffset(self, _):
        return self.zero

    def dst(self, _):
        return self.zero

    def tzname(self, _):
        return 'UTC'


try:
    utc = datetime.timezone.utc
except AttributeError:
    utc = Utc()