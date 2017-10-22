#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from datetime import datetime

import simplejson
import pytz
import sqlalchemy
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, create_engine
from sqlalchemy.ext import mutable
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from maic.constants import STATUS_FAILED, STATUS_PENDING, STATUS_RUNNING, STATUS_SUCCEEDED

Base = declarative_base()
Session = sessionmaker()


class TestStore(object):
    def __init__(self, connection=None, log=True):
        if not connection:
            connection = self._create_connection_str(
                os.environ.get('DB_HOST'),
                os.environ.get('DB_PORT'),
                os.environ.get('DB_NAME'),
                os.environ.get('DB_USER'),
                os.environ.get('DB_PASSWORD')
            )
        self.engine = create_engine(connection, echo=log)
        Session.configure(bind=self.engine)
        self.session = Session()
        Base.metadata.create_all(self.engine)

    def _create_connection_str(self, host, port, db, user, password):
        return 'postgresql://{}:{}@{}:{}/{}?sslmode=disable'.format(
            user, password, host, port, db
        )

    def create_run(self, name, environment=''):
        run = TestRun(name=name, environment=environment)
        self.session.add(run)
        self.session.commit()
        return run

    def save(self, instance):
        self.session.add(instance)
        self.session.commit()

    def save_many(self, _list):
        self.session.all_all(_list)
        self.session.commit()

    def export_run(self, run, include_cases=True):
        return run.export(include_cases)


class JsonEncodedDict(sqlalchemy.TypeDecorator):
    """
    Enables JSON storage by encoding and decoding on the fly.
    """
    impl = sqlalchemy.String

    def process_bind_param(self, value, dialect):
        return simplejson.dumps(value)

    def process_result_value(self, value, dialect):
        return simplejson.loads(value)

mutable.MutableDict.associate_with(JsonEncodedDict)


class TestRun(Base):
    __tablename__ = 'test_run'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    environment = Column(String(100), nullable=True)
    status = Column(String(15), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    cases = relationship("TestCase", back_populates="run")

    def __init__(self, name, environment):
        self.name = name
        self.environment = environment
        self.status = STATUS_PENDING
        self.started_at = None
        self.ended_at = None
        self.test_cases = []

    def __repr__(self):
        return 'Run {}:{} Status {} Time {} -> {}'.format(
            self.id, self.name, self.status, self.started_at, self.ended_at
        )

    def start(self):
        self.started_at = datetime.now(pytz.utc)
        self.status = STATUS_RUNNING

    def end(self, success=False):
        self.ended_at = datetime.now(pytz.utc)
        self.status = STATUS_SUCCEEDED if success else STATUS_FAILED

    def add_test(self, name, category):
        test_case = TestCase(name, category)
        test_case.run_id = self.id
        self._add_test_instance(test_case)
        return test_case

    def _add_test_instance(self, test):
        if not isinstance(test, TestCase):
            print('Not instance of TestCase! ignoring')
        self.test_cases.append(test)

    def mark_test_finished_by_name(self, name, category, success, details):
        for item in self.test_cases:
            if item.name == name and item.category == category and item.is_running():
                item.end(success, details)
                return item
        return None

    def has_succeeded(self):
        return self.status == STATUS_SUCCEEDED

    def export(self, include_cases=True):
        exported = {
            'id': self.id,
            'name': self.name,
            'success': self.has_succeeded(),
            'status': self.status,
            'started': self.started_at.isoformat() if self.started_at is not None else None,
            'ended': self.ended_at.isoformat() if self.ended_at is not None else None,
        }
        if include_cases:
            exported['cases'] = []
            for item in self.cases:
                exported['cases'].append(item.export())

        return exported


class TestCase(Base):
    __tablename__ = 'test_case'

    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey('test_run.id'))
    name = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)
    status = Column(String(15), nullable=False)
    details = Column(JsonEncodedDict, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    run = relationship('TestRun', back_populates='cases')
    data = None

    def __init__(self, name, category):
        self.name = name
        self.category = category
        self.status = STATUS_PENDING
        self.started_at = None
        self.ended_at = None
        self.data = None

    def __repr__(self):
        return 'Case {}:{} Run {} Status {} Time {} -> {}'.format(
            self.id, self.name, self.run_id, self.status, self.started_at, self.ended_at
        )

    def report(self):
        return 'Case {}:{} Status {}'.format(
            self.id, self.name, self.status
        )

    def start(self):
        self.started_at = datetime.now(pytz.utc)
        self.status = STATUS_RUNNING

    def end(self, success=False, details=None):
        self.ended_at = datetime.now(pytz.utc)
        self.details = details
        self.status = STATUS_SUCCEEDED if success else STATUS_FAILED

    def set_extra_data(self, data):
        self.data = data

    @property
    def extra_data(self):
        return self.data

    def is_running(self):
        return self.status == STATUS_RUNNING

    def is_pending(self):
        return self.status == STATUS_PENDING

    def is_running_or_pending(self):
        return self.is_running() or self.is_pending()

    def failed(self):
        return self.status == STATUS_FAILED

    def succeeded(self):
        return self.status == STATUS_SUCCEEDED

    def export(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'success': self.succeeded(),
            'status': self.status,
            'details': self.details,
            'started': self.started_at.isoformat() if self.started_at is not None else None,
            'ended': self.ended_at.isoformat() if self.ended_at is not None else None,
        }
