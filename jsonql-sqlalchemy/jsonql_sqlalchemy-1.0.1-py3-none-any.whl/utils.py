import sqlalchemy.sql.sqltypes as sqltypes
from . import types


__all__ = ["map_sqltypes"]


def map_sqltypes(column_type, **kwargs):
    """Mapping sqltype to JsonQL Data Type

    Args:
        column_type (sqltype): Type of SQLAlchemy Model Field
        tz (timezone): Default Timezone
        datetime_string_format (str): Default Datetime format string
        date_string_format (str): Default Date format string
    """

    if isinstance(column_type, sqltypes.Integer) \
            or isinstance(column_type, sqltypes.SmallInteger):
        return types.Integer()
    elif isinstance(column_type, sqltypes.String):
        return types.String()
    elif isinstance(column_type, sqltypes.DateTime):
        return types.DateTime(tz=kwargs.get("tz"),
                              string_format=kwargs.get("datetime_string_format"))
    elif isinstance(column_type, sqltypes.Date):
        return types.Date(tz=kwargs.get("tz"),
                          string_format=kwargs.get("date_string_format"))
    elif isinstance(column_type, sqltypes.Time):
        return types.Time(tz=kwargs.get("tz"))
    else:
        raise TypeError("Mapping failed: Unknown Column Type")


def map_model(sqlalchemy_model, **kwargs):
    """ Mapping SQLAlchemy Model Class to JsonQL Class

    Args:
        sqlalchemy_model (SQLAlchemy): SQLAlchemy Model Class
        tz (timezone): Default Timezone
        datetime_string_format (str): Default Datetime format string
        date_string_format (str): Default Date format string
    """

    mapped_fields = {}

    for column in sqlalchemy_model.__table__.columns:
        mapped_fields[column.name] = {
            "type": map_sqltypes(column.type, **kwargs),
            "auto_increment": str(column.autoincrement) == "True",
            "nullable": bool(column.nullable),
            "default": bool(column.default),
        }

    return mapped_fields
