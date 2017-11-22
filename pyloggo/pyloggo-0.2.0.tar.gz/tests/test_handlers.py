from pyloggo.handlers import MongoHandler, MongoSummaryHandler

from pymongo.errors import PyMongoError
import pymongo

import unittest
import logging
import time
import sys


class TestMongoHandler(unittest.TestCase):
    host_name = 'localhost'
    database_name = 'test_pyloggo'

    def setUp(self):
        self.handler = MongoHandler(host=self.host_name,
                                    database_name=self.database_name,
                                    )
        self.log = logging.getLogger('testLogger')
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(self.handler)

    def tearDown(self):
        self.handler.connection.drop_database(self.database_name)
        self.handler.close()
        self.log.removeHandler(self.handler)
        self.log = None
        self.handler = None

    def test_connect(self):
        handler = MongoHandler(host='localhost',
                               database_name=self.database_name)
        self.assertTrue(isinstance(handler, MongoHandler))
        self.handler.connection.drop_database(self.database_name)
        handler.close()

    def test_connect_failed_silent(self):
        import pyloggo.handlers
        pyloggo.handlers._connection = None
        kwargs = {'connectTimeoutMS': 2000, 'serverselectiontimeoutms': 2000}
        handler = MongoHandler(host='unknow_host',
                               database_name=self.database_name,
                               fail_silently=True,
                               **kwargs)
        self.assertTrue(isinstance(handler, MongoHandler))
        self.handler.connection.drop_database(self.database_name)
        handler.close()

    def test_emit(self):
        self.log.warning('test message')
        document = self.handler.collection.find_one(
            {'message': 'test message', 'level': 'WARNING'})
        assert document is not None
        self.assertEqual(document['message'], 'test message')
        self.assertEqual(document['level'], 'WARNING')

    def test_emit_exception(self):
        try:
            raise Exception('exc1')
        except:
            self.log.exception('test message')

        document = self.handler.collection.find_one(
            {'message': 'test message', 'level': 'ERROR'})
        assert document is not None
        self.assertEqual(document['message'], 'test message')
        self.assertEqual(document['level'], 'ERROR')
        self.assertEqual(document['exception']['message'], 'exc1')










 

