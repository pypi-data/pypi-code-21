# -*- coding=utf-8 -*-


import sys

sys.path.append('..')

import hammer
from hammer.sqlhelper import SqlHelper

db_config = {
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

if __name__ == '__main__':
    sql = SqlHelper(**db_config)

    fields = {
        'name': 'wo shi  lgq',
        'age': 24,
    }

    cond = {
        'id': 1
    }

    sql.update_json(fields, cond, table_name = 'test', commit = True)

    #
    #     sql.create_db('ttttt')
    #
    #     command = '''
    #     CREATE TABLE `test` (
    #   `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
    #   `name` char(255) DEFAULT NULL,
    #   `age` int(11) DEFAULT NULL,
    #   PRIMARY KEY (`id`)
    # ) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8;
    # '''
    #
    #
    #
    #     # command = 'INSERT INTO user (name, age) VALUES (%s, %s)'
    #
    #     # sql.insert_data(command, ('dfjakd', 1233), commit = True)
    #
    #     data = {
    #         'name': 'jfdjafl',
    #         'age': '102'
    #     }
    #
    #     # sql.insert_json(data, 'user', True)
    #
    #     datas = []
    #     datas.append(data)
    #     datas.append(data)
    #     datas.append(data)
    #     datas.append(data)
    #
    #     # sql.insert_json_list(datas, 'user', True)
    #
    #     command = 'SELECT * FROM user'
    #     result = sql.query(command)
    #     print(result)
    #
    #     result = sql.query_one(command)
    #     print(result)
