"""A holed layer over the sqlite3 API"""

__all__ = ["get_conn", "conn_is_open", "cursor_to_data_header", "cursor_to_rows", "MyDBRow",
           "TableInfo", "get_table_names", "get_table_info"]

from collections import OrderedDict
import sqlite3


def get_conn(filename):
    """Returns new sqlite3.Connection object with _dict_factory() as row factory"""
    conn = sqlite3.connect(filename)
    conn.row_factory = _dict_factory
    return conn


def conn_is_open(conn):
    """Tests sqlite3 connection, returns T/F"""
    if conn is None:
        return False

    try:
        get_table_names(conn)
        return True

        # # Idea taken from
        # # http: // stackoverflow.com / questions / 1981392 / how - to - tell - if -python - sqlite - database - connection - or -cursor - is -closed
        # conn.execute("select id from molecule limit 1")
        # return True
    except sqlite3.ProgrammingError as e:
        # print(e)
        return False

def get_table_names(conn):
    # http://stackoverflow.com/questions/305378/list-of-tables-db-schema-dump-etc-using-the-python-sqlite3-api

    r = conn.execute("select name from sqlite_master where type = 'table'")
    names = [row.name for row in r]
    return names


def cursor_to_data_header(cursor):
    """Fetches all rows from query ("cursor") and returns a pair (data, header)

    Returns: (data, header), where
        - data is a [num_rows]x[num_cols] list of lists;
        - header is a [num_cols] list containing the field names
    """
    n = 0
    data, header = [], {}
    for row in cursor:
        if n == 0:
            header = row.keys()
        data.append(row.values())
    return data, list(header)


def cursor_to_rows(cursor):
    """Fetches all rows from query ("cursor") and returns a list of MyDBRow objects
    """
    ret = []
    for row in cursor:
        ret.append(row)
    return ret


class MyDBRow(OrderedDict):
    """
    Dict subclass that allows attribute-like access of values using keys
    """
    def __getattribute__(self, name):
        """
        Allows attribute-like access of dictionary values
        """
        if name in self:
            return self[name]
        return OrderedDict.__getattribute__(self, name)
        # raise AttributeError("'{}' object has no attribute '{}' #".format(self.__class__.__name__, name))

    def None_to_zero(self):
        """Replace None with zero"""

        for key in self:
            if self[key] is None:
                self[key] = 0.


class TableInfo(OrderedDict):
    """
    Represents the information about a table in dict-like form where key is the field name
    """
    def find(self, **kwargs):
        """
        Finds row matching specific field value

        Args:
            **kwargs: (**only one argument accepted**) fielname=value, e.g., formula="OH"

        Returns: list element or None
        """

        if len(kwargs) != 1:
            raise ValueError("One and only one keyword argument accepted")

        key = list(kwargs.keys())[0]
        value = list(kwargs.values())[0]
        ret = None
        for row in self.values():
            if row[key] == value:
                ret = row
                break
        return ret


def get_table_info(conn, tablename):
    """Returns TableInfo object"""
    r = conn.execute("pragma table_info('{}')".format(tablename))
    ret = TableInfo(((row["name"], row) for row in r))
    return ret


# http://stackoverflow.com/questions/3300464/how-can-i-get-dict-from-sqlite-query
def _dict_factory(cursor, row):
    d = MyDBRow()
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

