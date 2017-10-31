from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from .db import db_connect

engine = create_engine(db_connect)
Base = declarative_base()


class Repo(Base):
    __tablename__ = 'repositories'

    name = Column(String)
    path = Column(String, primary_key=True)

    def __repr__(self):
        return "<Repo(name={name}, path={path})>".format(name=self.name, path=self.path)


Base.metadata.create_all(engine)
