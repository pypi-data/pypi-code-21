from sqlalchemy import (
    Table,
    Column,
    Index,
    Integer,
    Text,
    Unicode,UnicodeText,
    DateTime,
    ForeignKey,
    desc, asc,UniqueConstraint
)

from datetime import datetime,timedelta
import logging,uuid

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData
NAMING_CONVENTION = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base(metadata=metadata)



def initdb(session):
    Base.metadata.create_all(session.get_bind() )
    session.add(
        PPSsuser(username = u'admin',password = u'admin')
    )
    session.add(
        PPSsgroup(name = u"admin")
    )
    session.add(
        PPSspermission(name = u"admin")
    )

ppssuserlkppssgroup = Table('ppssuser_lk_ppssgroup', Base.metadata,
    Column('user_id',UnicodeText,ForeignKey('ppss_user.id')),
    Column('group_id',Integer,ForeignKey('ppss_group.id') )
)
ppssgrouplkppsspermission = Table('ppssgroup_lk_ppsspermission', Base.metadata,
    Column('group_id',UnicodeText,ForeignKey('ppss_group.id')),
    Column('permission_id',Integer,ForeignKey('ppss_permission.id') )
)
ppssgrouplkppsspermission = Table('ppssuser_lk_ppsspermission', Base.metadata,
    Column('user_id',UnicodeText,ForeignKey('ppss_user.id')),
    Column('permission_id',Integer,ForeignKey('ppss_permission.id') )
)


class PPSsuser(Base):
    __tablename__   = 'ppss_user'
    id              = Column(Integer, primary_key=True)
    username        = Column(Unicode(128))
    password        = Column(Unicode(512))

    @classmethod
    def checkLogin(cls,user,password,dbsession):
        res = dbsession.query(cls).filter(cls.username==user).filter(cls.password==password).first()
        return len(res)==1

class PPSsgroup(Base):
    __tablename__   = 'ppss_group'
    id     = Column(Integer, primary_key=True)
    name   = Column(Unicode(128))

class PPSspermission(Base):
    __tablename__   = 'ppss_permission'
    id     = Column(Integer, primary_key=True)
    name   = Column(Unicode(128))

