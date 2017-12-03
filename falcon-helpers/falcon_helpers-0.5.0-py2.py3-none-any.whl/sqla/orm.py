import sqlalchemy as sa
from sqlalchemy.schema import MetaData
from sqlalchemy.ext.declarative import as_declarative

from falcon_helpers.sqla.core import utcnow
from falcon_helpers.sqla.utils import random_data_for_type


convention = {
  "ix": 'ix_%(column_0_label)s',
  "uq": "uq_%(table_name)s_%(column_0_name)s",
  "ck": "ck_%(table_name)s_%(constraint_name)s",
  "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
  "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)


@as_declarative(metadata=metadata)
class ModelBase:
    pass


class BaseColumns:
    id = sa.Column(sa.Integer, primary_key=True, nullable=False)

    created_ts = sa.Column(sa.DateTime, server_default=utcnow())
    updated_ts = sa.Column(sa.DateTime, server_default=utcnow(),
                           server_onupdate=utcnow())


class Testable:

    @classmethod
    def testing_create(cls, **kwargs):
        """Create an object for testing with default data appropriate for the
        field type


        :param _numeric_defaults_range: a tuple of (HIGH, LOW) which controls
            the acceptable defaults of the number types. Both integer and
            numeric (float) fields are controlled by this setting. This is
            helpful when some fields have a constrained value.

        ATTRIBUTION: This was largely copied from the wonderful folks at Level
        12, they write high-class software, check them out: https://level12.io
        """

        NUMERIC_HIGH, NUMERIC_LOW = kwargs.pop('_numeric_defaults_range', (-100, 100))

        insp = sa.inspection.inspect(cls)

        def skippable(column):
            return (
                column.key in kwargs     # skip fields already in kwargs
                or column.foreign_keys   # skip foreign keys
                or column.server_default # skip fields with server defaults
                or column.default        # skip fields with defaults
                or column.primary_key)   # skip any primary key

        for column in (col for col in insp.columns if not skippable(col)):
            try:
                kwargs[column.key] = random_data_for_type(
                    column, NUMERIC_HIGH, NUMERIC_LOW)
            except ValueError:
                pass

        return cls(**kwargs)
