import logging
import io
import os

import portend
from jaraco.postgres import PostgresDatabase, PostgresServer


HOST = os.environ.get('HOST', 'localhost')


def __setup_logging():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    root.addHandler(handler)
__setup_logging()


class TestPostgresServer:
    def test_serves_postgres(self):
        port = portend.find_available_local_port()
        server = PostgresServer(HOST, port)
        server.initdb()

        try:
            server.start()
            version = server.get_version()

            assert len(version) > 0
            assert version[0] >= 8
        finally:
            server.destroy()

    def test_serves_postgres_with_locale(self):
        port = portend.find_available_local_port()
        server = PostgresServer(HOST, port)
        locale = 'C'
        server.initdb(locale=locale)

        try:
            server.start()
            server.get_version()  # To check we're able to talk to it.

            config = os.path.join(server.base_pathname, 'postgresql.conf')
            with io.open(config, encoding='utf-8') as strm:
                expect = "lc_messages = 'C'"
                assert any(expect in line for line in strm)
        finally:
            server.destroy()

    def test_unicode_value(self, monkeypatch):
        port = portend.find_available_local_port()
        monkeypatch.setitem(os.environ, 'LANG', 'C')
        server = PostgresServer(HOST, port)
        server.initdb()
        try:
            server.start()
            server.get_version()
            db = server.create('test_unicode')
            db.sql('CREATE TABLE records(name varchar(80))')
            db.sql("INSERT INTO records (name) VALUES (U&'\\2609')")
        finally:
            server.destroy()


class TestPostgresDatabase:
    def setup(self):
        self.port = portend.find_available_local_port()
        self.server = PostgresServer(HOST, self.port)
        self.server.initdb()
        self.server.start()

    def teardown(self):
        self.server.destroy()

    def test_creates_user_and_database(self):
        database = PostgresDatabase(
            'tests', user='john', host=HOST, port=self.port)

        database.create_user()
        database.create()

        rows = database.sql('SELECT 1')

        assert rows == [(1, )]
