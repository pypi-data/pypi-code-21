# -*- coding: utf-8 -*-
# Created by lijian on 2017/6/26.
import MySQLdb


class MysqlDB(object):
    def __init__(self, db_host, db_user, db_password, db_name, db_port,
                 db_charset="utf8", use_unicode=True,
                 cursorclass=None, autocommit=False):
        self.conn = MySQLdb.connect(db_host, db_user, db_password, db_name,
                                    port=int(db_port), charset=db_charset,
                                    use_unicode=use_unicode,
                                    autocommit=autocommit)
        self.cursor = self.create_cursor(cursorclass)

    def create_cursor(self, cursorclass=None):
        if cursorclass:
            return self.conn.cursor(cursorclass=cursorclass)
        else:
            return self.conn.cursor()

    def fetch_one(self):
        return self.cursor.fetchone()

    def fetch_many(self, size=None):
        return self.cursor.fetchmany(size)

    def fetch_all(self):
        return self.cursor.fetchall()

    # 关闭数据库连接
    def close_db_connection(self):
        if self.conn.open:
            self.cursor.close()
            self.conn.close()
