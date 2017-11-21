# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: MIT License
# File   : test_pool.py
# Date   : 2017-06-15 15-05
# Version: 0.1
# Description: description of this file.

import sys

sys.path.append("..")

import datetime
import logging
import string
import threading
import pandas as pd
import random
import time

from hammer.sqlhelper import SqlHelper
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

from hammer.pymysqlpool import ConnectionPool

logging.basicConfig(format = '[%(asctime)s][%(name)s][%(module)s.%(lineno)d][%(levelname)s] %(message)s',
                    datefmt = '%Y-%m-%d %H:%M:%S',
                    level = logging.INFO)

config = {
    'pool_name': 'test',
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'test',
    'pool_resize_boundary': 2,
    'enable_auto_resize': True,
    'max_pool_size': 1
}

queue_data = Queue(maxsize = 9000000000)
start_time = time.time()
is_return = False


def conn_pool():
    # pool = MySQLConnectionPool(**config)
    pool = ConnectionPool(**config)
    # pool.connect()
    # print(pool)
    return pool


insert_sql = 'INSERT INTO folder (name, icon_url, create_at) VALUES (%s, %s, %s)'
select_sql = 'SELECT * FROM folder ORDER BY id DESC LIMIT 10'
update_sql = ''
delete_sql = ''
truncate_sql = 'TRUNCATE folder'

name_factory = lambda: ''.join(random.sample(string.ascii_letters, random.randint(2, 10)))


def generate_data():
    while True:
        name = name_factory()
        data = ('folder_{}'.format(name), 'icon_{}.png'.format(name), datetime.datetime.now())
        queue_data.put(data)

        if is_return:
            return


def check_data():
    while True:
        print('queue_data len:%s' % queue_data.qsize())
        if is_return:
            return


def insert_data():
    while True:
        while not queue_data.empty():
            with conn_pool().connection() as conn:
                data = queue_data.get()
                result = conn.cursor().execute(insert_sql, data)
                conn.commit()

            if time.time() - start_time > 10:
                print('queue_data len:%s' % queue_data.qsize())
                return


def run():
    pool = ThreadPoolExecutor(15)
    [pool.submit(generate_data) for i in range(5)]
    [pool.submit(check_data) for i in range(1)]
    [pool.submit(insert_data) for i in range(2)]

    print('----------++++++++')


def test_insert_one():
    # with conn_pool().connection() as conn:
    #     name = name_factory()
    #     result = conn.cursor().execute(insert_sql, ('folder_{}'.format(name),
    #                                                 'icon_{}.png'.format(name),
    #                                                 datetime.datetime.now()))
    #     conn.commit()
    #
    # time.sleep(10)
    # with conn_pool().connection() as conn:
    #     name = name_factory()
    #     result = conn.cursor().execute(insert_sql, ('folder_{}'.format(name),
    #                                                 'icon_{}.png'.format(name),
    #                                                 datetime.datetime.now()))
    #     conn.commit()
    time.sleep(10)


def test_insert_many():
    with conn_pool().cursor() as cursor:
        folders = []

        for _ in range(10):
            name = name_factory()
            folders.append(('folder_{}'.format(name), 'icon_{}.png'.format(name), datetime.datetime.now()))
        result = cursor.executemany(insert_sql, folders)
        print(result)


def test_query():
    with conn_pool().cursor() as cursor:
        cursor.execute(select_sql)
        for item in sorted(cursor, key = lambda x: x['id']):
            print(item)
            # _ = item


def test_truncate():
    with conn_pool().cursor() as cursor:
        cursor.execute(truncate_sql)


def test_with_multi_threading():
    test_truncate()

    def task(n):
        th_id = threading.get_ident()
        print('In thread {}'.format(th_id))
        # for _ in range(n):
        with conn_pool().connection() as conn:
            while True:
                name = name_factory()
                result = conn.cursor().execute(insert_sql, ('folder_{}'.format(name),
                                                            'icon_{}.png'.format(name),
                                                            datetime.datetime.now(),
                                                            th_id))
                conn.commit()

    threads = [threading.Thread(target = task, args = (100,)) for _ in range(3)]
    for t in threads:
        t.start()

    for t in threads:
        t.join()

    test_query()


def test_borrow_return_connections():
    for _ in range(100000):
        with conn_pool().connection() as connection:
            _ = connection


def test_single_thread_insert():
    # with ping: 11s
    # without ping 11s
    test_truncate()
    for _ in range(5000):
        test_insert_one()

    test_query()


def test_query_with_pandas():
    import pandas as pd

    with conn_pool().connection() as conn:
        r = pd.read_sql(select_sql, conn)
        print(r)


if __name__ == '__main__':

    start = time.time()
    # test_insert_many()
    # test_query()
    test_insert_one()
    # test_query_with_pandas()
    # test_with_multi_threading()
    # test_single_thread_insert()
    # test_borrow_return_connections()

    time.sleep(1)
    print('Time consuming is {}'.format(time.time() - start))

    # run()
