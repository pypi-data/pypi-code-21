from six import iteritems

from schematics import types as sch_types
from schematics.undefined import Undefined

from sqlalchemy import types as sa_types, Column

from dmu_utils.schematics.types import NonUnicodeStringType, JSONType, CustomDecimalType


SCHEMATICS_TO_SQLALCHEMY_TYPE_MAP = {
    sch_types.StringType: sa_types.Unicode,
    NonUnicodeStringType: sa_types.String,
    sch_types.IntType: sa_types.Integer,
    sch_types.DateTimeType: sa_types.DateTime,
    # TODO(dmu) HIGH: Is sch_types.DecimalType really supported?
    sch_types.DecimalType: sa_types.Numeric,
    CustomDecimalType: sa_types.Numeric,
    sch_types.FloatType: sa_types.Float,
    sch_types.BooleanType: sa_types.Boolean,
    JSONType: sa_types.JSON,
    sch_types.ModelType: sa_types.JSON,
    sch_types.ListType: sa_types.JSON,
}


def get_sqlalchemy_type(schematics_type):
    sqlalchemy_type = SCHEMATICS_TO_SQLALCHEMY_TYPE_MAP.get(schematics_type)
    if sqlalchemy_type:
        return sqlalchemy_type

    for from_type, to_type in iteritems(SCHEMATICS_TO_SQLALCHEMY_TYPE_MAP):
        if issubclass(schematics_type, from_type):
            return to_type

    raise ValueError('Unsupported schematics type: {}'.format(schematics_type))


def schematics_field_to_sqlalchemy_column(field):
    schematics_type = type(field)
    sqlalchemy_type = get_sqlalchemy_type(schematics_type)

    kwargs = {}
    if issubclass(schematics_type, sch_types.StringType):
        kwargs['length'] = field.max_length

    if issubclass(schematics_type, CustomDecimalType):
        kwargs['precision'] = field.precision
        kwargs['scale'] = field.scale

    column_kwargs = {
        'nullable': not field.required
    }

    if field._default is not Undefined:
        column_kwargs['default'] = field._default

    return Column(sqlalchemy_type(**kwargs), **column_kwargs)
