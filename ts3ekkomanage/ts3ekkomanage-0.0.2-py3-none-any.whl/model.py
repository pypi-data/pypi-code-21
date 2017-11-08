from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Identity(Base):
    __tablename__ = 'identity'
    eid = Column(Integer, primary_key=True)
    unique_ts3_id = Column(String(100), nullable=False)
    private_identity = Column(String(100), nullable=False)

engine = create_engine('postgres://ekko:ekkopassword@dbhost/ekkodb')

Base.metadata.create_all(engine)

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()
