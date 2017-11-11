from pathlib import Path
import sqlite3

from .data_table import DataTable
from .data_view import DataView


class DataSession:
    _instance = None
    _name = None

    def __init__(self, conn):
        self._tables = {}        
        self._conn = conn
        cur = conn.cursor()
        sql = '''
        SELECT name
        FROM sqlite_master
        WHERE type = "table"
        '''
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        for row in rows:
            tblname = row[0]
            tbl = DataTable(conn, tblname)
            self._tables[tblname] = tbl

    @staticmethod
    def _get_or_make_datadir():
        datadir = Path.home() / '.avilabutils' / 'data'
        if not datadir.exists():
            datadir.mkdir(parents=True)
        return datadir

    @classmethod
    def _create_new_instance(cls, db):
        conn = sqlite3.connect(str(db), isolation_level=None)
        cls._instance = DataSession(conn)
        return cls._instance

    @classmethod
    def new(cls, name):
        datadir = cls._get_or_make_datadir()
        db = datadir / f'{name}.db'
        if db.exists():
            raise RuntimeError(f'{name} already exists!')
        cls._name = name
        return cls._create_new_instance(db)

    @classmethod
    def load(cls, name):
        if cls._instance and cls._name == name:
            return cls._instance

        datadir = cls._get_or_make_datadir()
        db = datadir / f'{name}.db'
        if not db.exists():
            raise RuntimeError(f'DataSession with name {name} not found!')
        cls._name = name
        return cls._create_new_instance(db)

    def table(self, name):
        if name not in self._tables:
            tbl = DataTable(self._conn, name)
            tbl.create()
            self._tables[name] = tbl
        return self._tables[name]

    def print_tables_info(self):
        for table in self._tables.values():
            print(table, end='\n\n')

    def clean(self):
        names = list(self._tables.keys())
        for name in names:
            self.del_table(name)

    def del_table(self, name):
        if name in self._tables:
            tbl = self._tables.pop(name)
            if tbl:
                cur = self._conn.cursor()
                cur.execute(f'DROP TABLE {name}')
                cur.close()

    def query(self, sql, params=None):
        cur = self._conn.cursor()
        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)
        view = DataView(cur, cur.fetchall())
        return view

    def close(self):
        self._conn.close()
