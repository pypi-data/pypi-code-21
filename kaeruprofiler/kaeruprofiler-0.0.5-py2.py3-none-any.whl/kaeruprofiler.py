import time
import sqlite3
from pprint import pprint


FILENAME = 'profile.db'


def open_db():
    conn = sqlite3.connect(FILENAME)
    return conn


def init():
    conn = open_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE main (
            keyname TEXT PRIMARY KEY, count INTEGER, time REAL)''')
    conn.close()


def show_sorted_profile():
    conn = open_db()
    c = conn.cursor()
    c.execute('''SELECT * FROM main ORDER BY time DESC''')
    pprint(c.fetchall())


def get_current_profile(conn, key):
    c = conn.cursor()
    q = "SELECT * FROM main WHERE keyname = '{}'".format(key)
    c.execute(q)
    return c.fetchone()


def write_new_profile(conn, key, elapsed):
    q = 'INSERT INTO main VALUES ({}, 1, {})'.format(key, elapsed)
    c = conn.cursor()
    c.execute(q)
    conn.commit()


def update_profile(conn, key, elapsed):
    q = (
        "UPDATE main SET count = count + 1,"
        "time = time + {} WHERE keyname = '{}'"
        .format(elapsed, key)
    )
    c = conn.cursor()
    c.execute(q)
    conn.commit()


def profile_with_key(attr_name):
    def each_profile(method):
        def get_current_attr(self, *args, **kwargs):
            splitted = attr_name.split('.')
            current_attr = self
            for sp in splitted:
                current_attr = getattr(current_attr, sp)
            return current_attr

        def _deco(self, *args, **kwargs):
            conn = open_db()

            current_attr = get_current_attr(self, *args, **kwargs)
            # data = loaded.get(current_attr, {'count': 0, 'time': 0})

            start = time.time()

            r = method(self, *args, **kwargs)

            end = time.time()
            elapsed = end - start

            current_profile = get_current_profile(conn, current_attr)
            if current_profile:
                update_profile(conn, current_attr, elapsed)
            else:
                write_new_profile(conn, current_attr, elapsed)
            conn.close()
            return r
        return _deco
    return each_profile
