import re

from sqlalchemy import MetaData, Column, Integer, CHAR
from sqlalchemy.ext.declarative import declared_attr, declarative_base

from baka_tenshi import util
from baka_tenshi.schema import References


__all__ = (
    'Base',
    'Model'
)

camelcase_re = re.compile(r'([A-Z]+)(?=[a-z0-9])')

def camel_to_snake_case(name):
    def _join(match):
        word = match.group()

        if len(word) > 1:
            return ('_%s_%s' % (word[:-1], word[-1])).lower()

        return '_' + word.lower()

    return camelcase_re.sub(_join, name).lstrip('_')


# Recommended naming convention used by Alembic, as various different database
# providers will autogenerate vastly different names making migrations more
# difficult. See: http://alembic.readthedocs.org/en/latest/naming.html
NAMING_CONVENTION = {
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "pk": "pk_%(table_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ix": "ix_%(table_name)s_%(column_0_name)s"
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)


class BaseMeta(References):
    @declared_attr
    def __tablename__(cls):
        return camel_to_snake_case(cls.__name__)

Base = declarative_base(cls=BaseMeta, metadata=metadata)

class ModelMeta(BaseMeta):

    id = Column(Integer, primary_key=True, autoincrement=True)
    pid = Column(CHAR(8), unique=True, default=util.generate)


Model = declarative_base(cls=ModelMeta, metadata=metadata)
