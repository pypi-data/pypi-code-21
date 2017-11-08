import pytz
from sqlalchemy import Column, String, types, text, \
    TypeDecorator, MetaData, Text
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.ext.declarative import declarative_base

meta = MetaData()
Base = declarative_base(metadata=meta)


class AwareDateTime(TypeDecorator):
    """Results returned as aware datetimes, not naive ones.
    """

    impl = types.DateTime

    def process_result_value(self, value, dialect):
        return value.replace(tzinfo=pytz.utc) if value else None


class BaseModel(Base):
    """
    Base class that have automatically
     - id column which is auto-incremented
     - creation_datetime set to CURRENT_TIMESTAMP when the row is created
     - modification_datetime set to CURRENT_TIMESTAMP when the row is modified
    """
    __abstract__ = True

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    creation_datetime = Column(AwareDateTime, server_default=text('CURRENT_TIMESTAMP'))
    modification_datetime = Column(AwareDateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))


class SchemaVersion(BaseModel):
    __tablename__ = "schema_version"

    version_code = Column(String(256), nullable=False)
    comment = Column(Text, nullable=False)
