import unittest
from dxpy.task import database


class TestDatabase(unittest.TestCase):
    def setUp(self):
        c = database.config
        c['path'] = ':memory:'
        database.Database.create()

    def tearDown(self):
        database.Database.clear()
        database.config.back_to_default()

    @unittest.skip
    def test_create_engine(self):
        database.Database().get_or_create_engine()

    def test_create_database(self):
        database.Database.create()
        database.Database.create()
        database.Database.clear()

    @unittest.skip
    def test_get_session(self):
        sess = database.Database().session()
        sess.query(database.TaskDB).all()
        sess.close()
