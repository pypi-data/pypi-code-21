import os
from abc import ABCMeta, abstractmethod

import pytest
from simple_settings import settings
from sqlalchemy.engine.url import make_url
from sqlalchemy_utils import drop_database, create_database, database_exists
from webtest import TestApp

from ingredients_db.database import Database


class APITestCase(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def app_cls(self):
        raise NotImplementedError

    @abstractmethod
    def setup_mounts(self, app):
        pass

    @abstractmethod
    def settings_module(self) -> str:
        raise NotImplementedError

    @pytest.fixture
    def uri(self):
        if 'CI' in os.environ:
            return "postgresql+psycopg2://postgres@127.0.0.1/test_db"
        else:
            return os.environ['TEST_DB_URL']

    @pytest.fixture
    def database(self, uri):
        if database_exists(uri):
            drop_database(uri)
        create_database(uri)
        yield
        drop_database(uri)

    def setup_database(self, uri):
        url = make_url(uri)
        database = Database(
            url.host,
            url.port,
            url.username,
            url.password,
            url.database,
            -1,
            migration_scripts_location='ingredients_db:alembic'
        )
        database.connect()
        database.engine.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
        database.engine.execute('CREATE EXTENSION IF NOT EXISTS "hstore"')
        database.upgrade("head")
        database.close()

    @pytest.yield_fixture()
    def app(self, database, uri):
        self.setup_database(uri)
        os.environ['settings'] = self.settings_module() + ",ingredients_http.test.settings.db_settings"
        settings._dict = {}  # Reset settings for every test
        app = self.app_cls()()
        self.setup_mounts(app)

        app.setup()

        yield app
        app.database.close()

    @pytest.yield_fixture()
    def wsgi(self, app):
        yield TestApp(app.wsgi_application)
