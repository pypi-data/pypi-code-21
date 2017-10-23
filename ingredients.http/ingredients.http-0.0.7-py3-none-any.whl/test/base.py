import os
from abc import ABCMeta, abstractmethod

import pytest
from simple_settings import settings
from sqlalchemy_utils import drop_database, create_database, database_exists
from webtest import TestApp


class APITestCase(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def router_cls(self):
        raise NotImplementedError

    @abstractmethod
    def setup_mounts(self, app):
        pass

    @abstractmethod
    def settings_module(self) -> str:
        raise NotImplementedError

    @pytest.fixture
    def database(self):
        if 'CI' in os.environ:
            uri = "postgresql+psycopg2://postgres@127.0.0.1/test_db"
        else:
            uri = os.environ['TEST_DB_URL']
        if database_exists(uri):
            drop_database(uri)
        create_database(uri)
        yield
        drop_database(uri)

    @pytest.yield_fixture()
    def app(self, database):
        os.environ['settings'] = self.settings_module() + ",ingredients_http.test.settings.db_settings"
        settings._dict = {}  # Reset settings for every test
        app = self.router_cls()()
        self.setup_mounts(app)

        app.setup()

        app.database.engine.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
        app.database.engine.execute('CREATE EXTENSION IF NOT EXISTS "hstore"')

        app.database.migration_scripts_location = 'ingredients_db:alembic'
        app.database.upgrade('head')
        yield app
        app.database.close()

    @pytest.yield_fixture()
    def wsgi(self, app):
        yield TestApp(app.wsgi_application)
