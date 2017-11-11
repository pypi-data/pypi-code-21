from collections import namedtuple

Column = namedtuple('Column', [
    'cid', 'name', 'type', 'notnull', 'dflt_value', 'pk'])


class DataTable:
    """Represents a table in SQLite.

    Provides methods to mutate the table like adding columns, adding and
    updating rows.
    """
    def _refresh_schema(self, cur):
        cur.execute(f'PRAGMA table_info([{self._name}])')
        for row in cur:
            name = row[1]
            self._cols[name] = Column(
                cid=row[0],
                name=row[1],
                type=row[2],
                notnull=row[3],
                dflt_value=row[4],
                pk=row[5]
            )

    def __init__(self, conn, name):
        """Loads the table if it exists

        If a table with the given name exists in the db, the constructor will
        load its schema. Otherwise it will simply instantiate an empty table
        structure.

        :param conn: A live SQL connection
        :param name: Name of the table
        """
        self._name = name
        self._conn = conn
        self._cols = {}
        cur = conn.cursor()
        self._refresh_schema(cur)
        cur.close()

    def __repr__(self):
        tbl = self._name + '- '
        for col in self._cols:
            tbl += f'\n{col}'
        return tbl

    def create(self):
        """Creates an almost empty table in the db

        Creates a table with a single column called _index. This column is
        supposed to be a proxy for the index into the dataset if the entire
        dataset were to be loaded in a list.
        """
        cur = self._conn.cursor()
        cur.execute(f'CREATE TABLE {self._name} (_index INTEGER PRIMARY KEY)')
        self._refresh_schema(cur)
        cur.close()

    def add_column(self, name, dtype):
        """Adds a new column to the table

        Regardless of whether this is an old table or a newly created one,
        this method adds a new empty column to the table.
        :param name: Name of the column
        :param dtype: Data type of the column, any SQLite type is allowed
        """
        cur = self._conn.cursor()        
        cur.execute(f'ALTER TABLE {self._name} add {name} {dtype}')
        self._refresh_schema(cur)
        cur.close()

    def append_rows(self, rows):
        """Adds new rows to the table

        :param rows: A list of dict like object with the column names in the 
        table as keys. It assumes that the data types in the rows are legit. If
        the _index column is present, it is ignored.
        """
        colnames = list(self._cols.keys())
        colnames.remove('_index')
        all_colnames = ','.join(colnames)
        val_placeholders = ','.join(['?'] * len(colnames))
        sql = f'''
        INSERT INTO {self._name} ({all_colnames})
        VALUES ({val_placeholders})
        '''
        ins_rows = []
        for row in rows:
            ins_row = []
            for colname in colnames:
                ins_row.append(row[colname])
            ins_rows.append(ins_row)
        cur = self._conn.cursor()
        cur.executemany(sql, ins_rows)
        cur.close()

    def update_rows(self, rows, cols_to_update):
        """Update the specified columns in the given rows

        Updates the rows identified by their _index column (key).
        :param rows: A list of dict-like objects. It may have any number of
        keys but only the keys specified in the cols_to_update list are
        considered. All other keys are ignored.
        :param cols_to_update: Columns that are to be updated. Only these keys
        are considered in the given rows. It is expected that these keys will
        be present.
        """
        for col_to_update in cols_to_update:
            if col_to_update not in self._cols:
                raise RuntimeError(f'Unknown column {col_to_update}!')

        sql_frags = []
        for col_to_update in cols_to_update:
            sql_frags.append(f'{col_to_update} = ?')
        sql_frag = ','.join(sql_frags)
        sql = f'UPDATE {self._name} SET {sql_frag} WHERE _index = ?'

        up_rows = []
        for row in rows:
            up_row = []
            for col_to_update in cols_to_update:
                up_row.append(row[col_to_update])
            up_row.append(row['_index'])
            up_rows.append(up_row)

        cur = self._conn.cursor()
        cur.executemany(sql, up_rows)
        cur.close()
