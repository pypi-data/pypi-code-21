from django.db import connections
import cx_Oracle



class DBHelper(object):
    
    def __init__(self, dbName):
        self.dbName = dbName
        
    def _getConnection(self):
        return connections[self.dbName]
        
    def fetchall(self, sql, parameters=None):
        with self._getConnection().cursor() as cursor:
            if parameters:
                cursor.execute(sql, parameters)
            else:
                cursor.execute(sql)
            return dictfetchall(cursor)
        
    def fetchone(self, sql, parameters=None):
        with self._getConnection().cursor() as cursor:
            if parameters:
                cursor.execute(sql, parameters)
            else:
                cursor.execute(sql)
            return dictfetchone(cursor)

    def execmany(self, sql, parameters=None):
        with self._getConnection().cursor() as cursor:
            if parameters:
                cursor.executemany(sql, parameters)

            else:
                cursor.executemany(sql)
            return cursor.description

    def execone(self, sql, parameters=None):
        with self._getConnection().cursor() as cursor:
            if parameters:
                cursor.execute(sql,parameters)
            else:
                cursor.execute(sql)
            return cursor

        
def dictfetchall(cursor):
    desc = cursor.description
    return [
        dict(zip([col[0].lower() for col in desc], row))
        for row in cursor.fetchall()
    ]

def dictfetchone(cursor):
    desc = cursor.description
    row = cursor.fetchone()
    if (row == None):
        return None
    return dict(zip([col[0].lower() for col in desc], row))
