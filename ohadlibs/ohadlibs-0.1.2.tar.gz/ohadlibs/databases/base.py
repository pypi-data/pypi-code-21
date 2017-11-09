import sqlite3


class DBSession:

    def __init__(self, path, query_name):
        self.path = path
        self.query_name = query_name

    def query(self, _query, _commit):
        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        res = c.execute(_query)
        if _commit:
            conn.commit()
        myres = list(res)
        conn.close()
        return myres

    def create_table(self, _table_name, _columns_types_dict):
        return self.query(self.compose_create_table_command(_table_name, _columns_types_dict), True)

    def insert(self, _table, _values_dict):
        return self.query(self.compose_insert_command(_table, _values_dict), True)

    def update(self, _table, _updated_values_dict, _where_values_dict, _where_operator):
        _q = "UPDATE {} SET {} WHERE {}".format(_table, self.set_values_to_string(_updated_values_dict),
                                                self.where_values_to_string(_where_values_dict, _where_operator))
        return self.query(_q, True)

    def is_in_db(self, _table, _count_field, _where_values_dict, _where_operator):
        _q = "SELECT COUNT(DISTINCT {}) FROM {} WHERE {}".format(_count_field, _table,
                                                                 self.where_values_to_string(_where_values_dict,
                                                                                             _where_operator))
        res = self.query(_q, False)
        return not res[0][0] == 0

    def insert_or_update(self, _table, ws_id, _values_dict):
        if self.is_in_db(_table, 'sha1', {'ws_id': ws_id}):
            self.update(_table, _values_dict, {'ws_id': ws_id}, 'AND')
        else:
            self.insert(_table, _values_dict)

    def select(self, distinct_bool, _table, _where_values_dict, _where_operator):
        res = self.query("pragma table_info({})".format(_table), False)
        _headers = [r[1] for r in res]
        if distinct_bool:
            distinct = "DISTINCT"
        else:
            distinct = ""
        if _where_values_dict == {}:
            q = "SELECT {} * FROM {}".format(distinct, _table)
        else:
            q = "SELECT {} * FROM {} WHERE {}".format(distinct, _table, self.where_values_to_string(_where_values_dict,
                                                                                                    _where_operator))
        _rows = self.query(q, False)
        return [dict(list(zip(_headers, row))) for row in _rows]

    # Static Methods

    @staticmethod
    def where_values_to_string(_values_dict, _operator):
        return " {} ".format(_operator).join(['='.join([list(i)[0].strip("t_"), "'{}'".format(list(i)[1])]) for i
                                              in list(_values_dict.items())])

    @staticmethod
    def set_values_to_string(_values_dict):
        return "{}".format(", ").join(['='.join([list(i)[0].strip("t_"), "'{}'".format(list(i)[1])]) for i in
                                       list(_values_dict.items())])

    @staticmethod
    def compose_insert_command(_table, _values_dict):
        cols_str = ", ".join([v[0].strip("t_") for v in _values_dict.items()])
        values_str = ", ".join(["'{}'".format(v[1].strip("}'")) for v in _values_dict.items()])
        q = "INSERT INTO {} ({}) VALUES ({})".format(_table, cols_str, values_str)
        return q

    @staticmethod
    def compose_create_table_command(_table, _columns_types_dict):
        cols = ', '.join([' '.join([v.strip("t_") for v in list(r)]) for r in _columns_types_dict.items()])
        q = "CREATE TABLE {} (id INTEGER PRIMARY KEY, {}) ".format(_table, cols)
        return q

