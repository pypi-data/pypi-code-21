# coding: utf-8
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from oslo_db.sqlalchemy import models

BASE = declarative_base()


class TestData(models.ModelBase, BASE):
    __tablename__ = 'test_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    data = Column(String(256), nullable=False)
