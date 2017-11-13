# -------------------------------------------------------------------------------
# Licence:
# Copyright (c) 2012-2017 Luzzi Valerio 
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
#
# Name:        sqlitedb.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     26/07/2017
# -------------------------------------------------------------------------------

from databases import *
from datatypes import *
from filesystem import *
import csv
import inspect
import sqlite3 as sqlite

class SqliteDB(AbstractDB):
    CORE_FUNCTIONS = ["ABS", "CHANGES", "CHAR", "COALESCE", "GLOB", "HEX", "IFNULL", "INSTR", "LAST_INSERT_ROWID",
                      "LENGTH", "LIKE", "LIKE", "LIKELIHOOD", "LIKELY", "LOAD_EXTENSION", "LOAD_EXTENSION", "LOWER",
                      "LTRIM", "LTRIM", "MAX", "MIN", "NULLIF", "PRINTF", "QUOTE", "RANDOM", "RANDOMBLOB", "REPLACE",
                      "ROUND", "ROUND", "RTRIM", "RTRIM", "SOUNDEX", "SQLITE_COMPILEOPTION_GET",
                      "SQLITE_COMPILEOPTION_USED", "SQLITE_SOURCE_ID", "SQLITE_VERSION", "SUBSTR", "SUBSTR",
                      "TOTAL_CHANGES", "TRIM", "TRIM", "TYPEOF", "UNICODE", "UNLIKELY", "UPPER", "ZEROBLOB"]
    AGGREGATE_FUNCTIONS = ["AVG", "COUNT", "GROUP_CONCAT", "MAX", "MIN", "SUM", "TOTAL"]
    DATE_FUNCTIONS = ["DATE", "TIME", "DATETIME", "JULIANDAY", "STRFTIME"]
    SPATIAL_FUNCTIONS = ["GEOMFROMTEXT", "GEOMFROMWKB", "ASTEXT", "POINT", "X", "Y"]
    RESERVED_WORDS = ["ABORT", "ACTION", "ADD", "AFTER", "ALL", "ALTER", "ANALYZE", "AND", "AS", "ASC", "ATTACH",
                      "AUTOINCREMENT", "BEFORE", "BEGIN", "BETWEEN", "BY", "CASCADE", "CASE", "CAST", "CHECK",
                      "COLLATE", "COLUMN", "COMMIT", "CONFLICT", "CONSTRAINT", "CREATE", "CROSS", "CURRENT_DATE",
                      "CURRENT_TIME", "CURRENT_TIMESTAMP", "DATABASE", "DEFAULT", "DEFERRABLE", "DEFERRED", "DELETE",
                      "DESC", "DETACH", "DISTINCT", "DROP", "EACH", "ELSE", "END", "ESCAPE", "EXCEPT", "EXCLUSIVE",
                      "EXISTS", "EXPLAIN", "FAIL", "FOR", "FOREIGN", "FROM", "FULL", "GLOB", "GROUP", "HAVING", "IF",
                      "IGNORE", "IMMEDIATE", "IN", "INDEX", "INDEXED", "INITIALLY", "INNER", "INSERT", "INSTEAD",
                      "INTERSECT", "INTO", "IS", "ISNULL", "JOIN", "KEY", "LEFT", "LIKE", "LIMIT", "MATCH", "NATURAL",
                      "NO", "NOT", "NOTNULL", "NULL", "OF", "OFFSET", "ON", "OR", "ORDER", "OUTER", "PLAN", "PRAGMA",
                      "PRIMARY", "QUERY", "RAISE", "RECURSIVE", "REFERENCES", "REGEXP", "REINDEX", "RELEASE", "RENAME",
                      "REPLACE", "RESTRICT", "RIGHT", "ROLLBACK", "ROW", "SAVEPOINT", "SELECT", "SET", "TABLE", "TEMP",
                      "TEMPORARY", "THEN", "TO", "TRANSACTION", "TRIGGER", "UNION", "UNIQUE", "UPDATE", "USING",
                      "VACUUM", "VALUES", "VIEW", "VIRTUAL", "WHEN", "WHERE", "WITH", "WITHOUT"]

    SQLITE_FUNCTIONS = CORE_FUNCTIONS + AGGREGATE_FUNCTIONS + DATE_FUNCTIONS + SPATIAL_FUNCTIONS + RESERVED_WORDS


    def __init__(self, filename, modules =[]):
        """
        Constructor
        :param filename:
        """
        AbstractDB.__init__(self, filename)
        self.pragma("synchronous=OFF")
        self.pragma("journal_mode=WAL")
        self.pragma("foreign_keys=ON")
        self.pragma("cache_size=4000")
        self.load_extension(modules)

    def pragma(self, text, env={}, verbose=False):
        """
        pragma
        """
        return self.execute("PRAGMA " + text, env, verbose=verbose)


    def create_function(self, func, nargs, fname):
        """
        create_function
        """
        self.conn.create_function(func, nargs, fname)


    def create_aggregate(self, func, nargs, fname):
        """
        create_aggregate
        """
        self.conn.create_aggregate(func, nargs, fname)

    def load_extension(self,modules):
        """
        load_extension
        """
        self.conn.enable_load_extension(True)
        for module in listify(modules):
            self.conn.execute("SELECT load_extension('%s')"%(module))
        self.conn.enable_load_extension(False)

    def load_function(self, modulename="gecosistema_lite", fnames="", verbose=False):
        """
        load_function
        """
        try:
            module = __import__(modulename)
            for fname in listify(fnames):
                try:
                    obj = getattr(module, fname)

                    if inspect.isfunction(obj):
                        n = len(inspect.getargspec(obj).args)
                        self.create_function(fname, n, obj)
                        if verbose:
                            print "load function %s(%s)" % (fname, n)
                    elif inspect.isclass(obj) and "step" in dir(obj):
                        fstep = getattr(obj, "step")
                        n = len(inspect.getargspec(fstep).args) - 1
                        self.create_aggregate(fname, n, obj)
                        if verbose:
                            print "load aggregate function %s(%s)" % (fname, n)
                except:
                    if verbose:
                        print "function <%s> not found." % (fname)
        except:
            if verbose:
                print "module <%s> not found. searching <%s>" % (modulename, fnames)

    def load_functions(self, sql, verbose=True):
        """
        load functions or aggregates
        ## from numpy import sqrt
        """
        sql = sql.replace(";", "\n")
        directives = re.findall(r'^\s*(?:#{1,2})\s*from\s+\w+\s+import\s+(?:\*|\w+).*', sql, re.I | re.M)
        directives = [normalizestring(item).strip('# ') for item in directives]

        for line in directives:
            print line.split(" ", 3)
            _from, module, _import, functions = line.split(" ", 3)
            if functions == "*":
                functions = re.findall(r'\w+\s*\(', sql, re.MULTILINE)
                functions = [fname.strip("( ") for fname in functions]
                functions = [fname for fname in functions if fname.upper() not in self.SQLITE_FUNCTIONS]
                functions = list(set(functions))
            self.load_function(module, functions, verbose)


    def __connect__(self):
        """
        Connect to the sqlite instance
        """
        try:
            self.conn = sqlite.connect(self.dsn)

        except sqlite.Error as err:
            print(err)
            self.close()


    def __del__(self):
        """
        Destructor
        """
        self.close()

    def GetTables(self, like="%"):
        """
        Return a list with all tablenames
        """
        sql = """
        SELECT tbl_name FROM sqlite_master      WHERE type IN ('table','view') AND tbl_name LIKE '{like}'
        UNION 
        SELECT tbl_name FROM sqlite_temp_master WHERE type IN ('table','view') AND tbl_name LIKE '{like}';""";
        env = {"like": like}
        table_list = self.execute(sql, env, verbose=False)
        table_list = [item[0] for item in table_list]
        return table_list

    def GetDDL(self, tablename, type="table,view,index", verbose=False):
        """
        Return DDL statements for tablename
        """
        type = ",".join(wrap(listify(type), "'"))
        env = {"tablename": tablename}
        statements = self.execute("""
        SELECT sql,[type] FROM sqlite_master      WHERE tbl_name='{tablename}' AND [type] IN (%s) AND NOT sql IS NULL 
        UNION
        SELECT sql,[type] FROM sqlite_temp_master WHERE tbl_name='{tablename}' AND [type] IN (%s) AND NOT sql IS NULL
        ORDER BY [type] DESC
        ;
        """ % (type, type), env, verbose=verbose)
        res = []
        for statement in statements:
            res.append(statement[0])
        return ";".join(res)


    def copy(self, tablename, data=True):
        """
        Create a copy of table
        """
        new_name = tablename + "-copy"
        env = {"tablename": tablename, "new_name": new_name}
        sql = """DROP TABLE IF EXISTS [{new_name}];DROP VIEW IF EXISTS [{new_name}];"""
        sql += self.GetDDL(tablename)
        sql = re.sub(r'\[' + tablename + r'\]', "[{new_name}]", sql, flags=re.I)
        sql = re.sub(r'INDEX \[(.*?)\]', r'INDEX [\1-copy]', sql, flags=re.I)
        if data:
            sql += """;INSERT OR REPLACE INTO [{new_name}] SELECT * FROM [{tablename}];"""
        self.execute(sql, env, verbose=True)
        return new_name

    def safe_name(self, columnname):

        columnname = re.sub("'", "''", columnname)
        columnname = re.sub("\[", "(", columnname)
        columnname = re.sub("\]", ")", columnname)
        columnname = columnname + "(1)" if (columnname.upper() in self.SQLITE_FUNCTIONS) else columnname
        return columnname

    def drop_column(self, tablename, columnnames, verbose=False):
        """
        Drop a column recreating the table
        """
        columnnames = listify(columnnames, ",")
        columnnames = [columnname for columnname in columnnames if
                       self.is_column(tablename, columnname) and not self.is_primary_key(tablename, columnname)]

        fieldnames = self.GetFieldNames(tablename)
        fieldnames = [item for item in fieldnames if item.lower() not in lower(columnnames)]
        sfieldnames = ",".join(wrap(fieldnames, "[", "]"))

        sql_create = self.GetDDL(tablename) + ";"
        # following line remove  the columnname from the create command

        # normalize the string
        sql_create = re.sub(r'\s+', ' ', sql_create)

        for columnname in columnnames:
            # remove column definition from create command
            ctype = self.GetColumnType(tablename, columnname)
            sql_create = sql_create.replace("[" + columnname + "] " + ctype, "")
            sql_create = sql_create.replace("[" + columnname + "]", "")
            sql_create = re.sub(r',\s*,', ',', sql_create)  # set ,, comas troubles
            sql_create = re.sub(r'\(\s*,', '(', sql_create)
            sql_create = re.sub(r',\s*\)', ')', sql_create)

        # this rename the command with a new name
        sql_create = re.sub(r'[\["]' + tablename + r'["\]]', "[{new_name}]", sql_create, flags=re.I)  # rename the table

        sql = """
        DROP  TABLE IF EXISTS [{new_name}];""" + sql_create + """
        INSERT OR REPLACE INTO [{new_name}] 
            SELECT {sfieldnames} FROM [{tablename}];
        DROP  TABLE [{tablename}];
        ALTER TABLE [{new_name}] RENAME TO [{tablename}];
        """
        env = {"tablename": tablename, "new_name": tempname("tmp-"), "sfieldnames": sfieldnames}


        self.execute(sql, env, verbose=verbose)
        return True

    def GetFieldNames(self, tablename, ctype=""):
        """
        GetFieldNames
        """
        env = {"tablename": tablename.strip("[]")}
        sql = """PRAGMA table_info([{tablename}])"""
        info = self.execute(sql, env)
        if not ctype:
            return [name for (cid, name, ftype, notnull, dflt_value, pk) in info]
        else:
            return [name for (cid, name, ftype, notnull, dflt_value, pk) in info if (ftype in ctype)]

    def GetColumnType(self, tablename, fieldnames=""):
        """
        GetColumnType
        """
        env = {"tablename": tablename.strip("[]")}
        info = self.pragma("table_info([{tablename}])", env)
        fieldnames = listify(fieldnames, ",")
        fieldnames = fieldnames if fieldnames else self.GetFieldNames(tablename)
        fieldnames = lower(fieldnames)
        info = [ftype for (cid, name, ftype, notnull, dflt_value, pk) in info if name.lower() in fieldnames]
        if len(info) == 0:
            return None
        elif len(info) == 1:
            return info[0]
        else:
            return info


    def GetPrimaryKeys(self, tablename):
        """
        GetPrimaryKeys
        """
        env = {"tablename": tablename.strip("[]")}
        sql = """PRAGMA table_info([{tablename}])"""
        info = self.execute(sql, env)
        return [name for (cid, name, type, notnull, dflt_value, pk) in info if pk > 0]


    def tableExists(self, tablename):
        """
        Check if tablename exists
        Return a boolean
        """
        env = {"tablename": tablename.strip("[]")}
        count = self.executeScalar("""SELECT COUNT(*) FROM
            (   SELECT * FROM sqlite_master WHERE type='table'      AND tbl_name='{tablename}' UNION
                SELECT * FROM sqlite_temp_master WHERE type='table' AND tbl_name='{tablename}')""", env)
        return count > 0

    def add_column(self, tablename, columnname, typename="TEXT", verbose=False):
        """
        add_column
        """
        env = {"tablename": tablename.strip("[]"), "columnname": columnname, "typename": typename}
        sql = """ALTER TABLE [{tablename}] ADD COLUMN [{columnname}] {typename};"""
        self.execute(sql, env, verbose=verbose)

    def is_column(self, tablename, columnname):
        """
        is_column - check if the column exists
        """
        env = {"tablename": tablename.strip("[]")}
        info = self.pragma("table_info([{tablename}])", env)
        fieldnames = [name for (cid, name, ftype, notnull, dflt_value, pk) in info]
        return lower(columnname) in lower(fieldnames)

    def is_primary_key(self, tablename, columnname):
        """
        is_primary_key
        """
        return columnname.lower() in lower(self.GetPrimaryKeys(tablename))

    def execute(self, sql, environ={}, outputmode="array", keepdims=True, commit=True, verbose=False):
        """
        execute
        """
        self.load_functions(sql)
        return AbstractDB.execute(self, sql, environ, outputmode, keepdims, commit, verbose)


    def executeScalar(self, sql, environ={}, commit=True, verbose=False):
        """
        executeScalar
        """
        self.load_functions(sql)
        return AbstractDB.executeScalar(self, sql, environ, commit, verbose)


    def insertMany(self, tablename, values, commit=True, verbose=False):
        """
        insertMany
        """
        if isinstance(values, (tuple, list,)) and len(values) > 0:
            # list of tuples
            if isinstance(values[0], (tuple, list,)):
                n = len(values[0])
                env = {"tablename": tablename, "question_marks": ",".join(["?"] * n)}
                sql = """INSERT OR REPLACE INTO [{tablename}] VALUES({question_marks});"""
            # list of objects
            elif isinstance(values[0], (dict,)):
                fieldnames = [item for item in values[0].keys() if item in self.GetFieldNames(tablename)]
                data = []
                for row in values:
                    data.append([row[key] for key in fieldnames])

                n = len(fieldnames)
                env = {"tablename": tablename, "fieldnames": ",".join(wrap(fieldnames, "[", "]")),
                       "question_marks": ",".join(["?"] * n)}
                sql = """INSERT OR REPLACE INTO [{tablename}]({fieldnames}) VALUES({question_marks});"""
                values = data

        self.executeMany(sql, env, values, commit, verbose)

    def count_null(self, tablename, columnname):
        """
        count_null
        """
        env = {"tablename": tablename, "columnname": columnname}
        return self.execute("""SELECT COUNT(*) FROM [{tablename}] WHERE [{columnname}] IS NULL;""", env, keepdims=False)

    def createTableFromCSV(self, filename, tablename, append=False, sep=";", primarykeys="", Temp=False, nodata=["Na"],
                           verbose=False):
        """
        createTableFromCSV - make a read-pass to detect data fieldtype
        """
        primarykeys = listify(primarykeys)
        # ---------------------------------------------------------------------------
        #   Open the stream
        # ---------------------------------------------------------------------------
        with open(filename, "rb") as stream:
            # ---------------------------------------------------------------------------
            #   decode data lines
            # ---------------------------------------------------------------------------
            fieldnames = []
            fieldtypes = []
            n = 1
            line_no = 0
            header_line_no = 0
            csvreader = csv.reader(stream, delimiter=sep, quotechar='"')

            for line in csvreader:
                line = [unicode(cell, 'utf-8-sig') for cell in line]
                if len(line) < n:
                    # skip empty lines
                    pass
                elif not fieldtypes:
                    n = len(line)
                    fieldtypes = [''] * n
                    fieldnames = line
                    header_line_no = line_no
                else:
                    fieldtypes = [SQLTYPES[min(SQLTYPES[item1], SQLTYPES[item2])] for (item1, item2) in
                                  zip(sqltype(line, nodata=nodata), fieldtypes)]

                line_no += 1

            self.createTable(tablename, fieldnames, fieldtypes, primarykeys, overwrite=not append, verbose=verbose)
            return (fieldnames, fieldtypes, header_line_no)

    def importCsv(self, filename, sep=";",
                  tablename=None,
                  primarykeys="",
                  guess_primary_key=True,
                  append=False, Temp=False,
                  nodata=["", "Na", "NaN", "-", "--", "N/A"], verbose=False):
        """
        importCsv
        """

        tablename = tablename if tablename else juststem(filename)
        (fieldnames, fieldtypes, header_line_no) = self.createTableFromCSV(filename, tablename, append, sep,
                                                                           primarykeys, Temp, nodata, verbose)
        # ---------------------------------------------------------------------------
        #   Open the stream
        # ---------------------------------------------------------------------------
        data = []
        n = len(fieldnames)
        line_no = 0
        with open(filename, "rb") as stream:
            csvreader = csv.reader(stream, delimiter=sep, quotechar='"')

            for line in csvreader:
                if line_no > header_line_no:
                    line = [unicode(cell, 'utf-8-sig') for cell in line]
                    if len(line) == n:
                        data.append(line)
                line_no += 1

            values = [parseValue(row) for row in data]
            self.insertMany(tablename, values, verbose=verbose)

    def importNumpy(self, data, tablename, append=True, Temp=False,
                    nodata=["", "Na", "NaN", "-", "--", "N/A"],
                    verbose=False):
        """
        importNumpy
        """
        m, n = data.shape
        values = [parseValue(data[i]) for i in range(m)]
        self.insertMany(tablename, values, verbose=verbose)

    def csv2Numpy(self, filename, sep=',', header_line_no=0):
        """
        csv2Numpy - load filecsv in to matrix of cell
        """
        data = []
        line_no = 0
        n = -1
        with open(filename, "rb") as stream:
            csvreader = csv.reader(stream, delimiter=sep, quotechar='"')

            for line in csvreader:
                if line_no > header_line_no:
                    line = [unicode(cell, 'utf-8-sig') for cell in line]
                    n = len(line) if n < 0 else n  # initialize n
                    if len(line) == n:
                        data.append(line)
                line_no += 1

            data = [parseValue(row) for row in data]
            data = np.array(data)
        return data


    def excel2Numpy(self, sheet, justvalues=False):
        """
        excel2Numpy - load excel in to matrix of cell
        """
        cellMatrix = []
        m, n = sheet.nrows, sheet.ncols
        for i in range(m):
            row = sheet.row_slice(i, start_colx=0, end_colx=None)

            # Date conversion
            # for j in range(n):
            #   if row[j].ctype == xlrd.XL_CELL_DATE:
            #       row[j].value = xlrd.xldate_as_datetime(row[j].value,0)

            if justvalues:
                row = [item.value for item in row]

            cellMatrix.append(row)
        # ------------------------------------------------------
        # Following lines explodes merged cells
        for (i0, i1, j0, j1) in sheet.merged_cells:
            for i in xrange(i0, i1):
                for j in xrange(j0, j1):
                    # cell (rlo, clo) (the top left one) will carry the data
                    # and formatting info; the remainder will be recorded as
                    # blank cells, but a renderer will apply the formatting info
                    # for the top left cell (e.g. border, pattern) to all cells in
                    # the range.
                    cell = sheet.cell(i0, j0).value if justvalues else sheet.cell(i0, j0)
                    cellMatrix[i][j] = cell
        # ------------------------------------------------------


        cellMatrix = np.array(cellMatrix)

        return np.array(cellMatrix)

    def createTableFromXls(self, filename, sheetname, append=False,
                           primarykeys="",
                           guess_primary_key=True,
                           Temp=False,
                           nodata=["", "Na", "NaN", "-", "--", "---", "N/A"],
                           verbose=False):
        """
        createTableFromXls - make a read-pass to detect data fieldtype
        """
        primarykeys = listify(primarykeys)
        nodata = listify(nodata,",")
        data = []
        header_line_no = 0
        with xlrd.open_workbook(filename) as wb:
            sheet = wb.sheet_by_name(sheetname)
            cellMatrix = self.excel2Numpy(sheet)
            vMatrix = np.empty_like(cellMatrix)
            m, n = cellMatrix.shape if len(cellMatrix.shape) == 2 else (0,0)


            #search for header line
            fieldnames = ["field%d" % j for j in range(n)]
            for i in range(m):
                header = sheet.row_slice(i, start_colx=0, end_colx=None)
                header = [item.value for item in header if item.ctype == xlrd.XL_CELL_TEXT]

                if len(header) == n:
                    fieldnames = header
                    #TO DO check safe names for sqlite
                    header_line_no = i
                    break

            fieldtypes = [9999] * n
            for i in range(header_line_no + 1, m):
                vMatrix[i, :] = xlsvalue(cellMatrix[i][:], nodata)

                fieldtypes = [SQLTYPES[min(SQLTYPES[item1], SQLTYPES[item2])] for item1, item2 in
                              zip(sqltype(cellMatrix[i][:], nodata=nodata), fieldtypes)]

            # guess primary key
            if guess_primary_key:
                idx_candidates = self.guessPrimaryKey(filename, sheetname, header_line_no, nodata)
                primarykeys = [fieldnames[idx] for idx in idx_candidates]

            if verbose:
                print "primarykeys=", primarykeys

            self.createTable(sheetname, fieldnames, fieldtypes, primarykeys, overwrite=not append, verbose=verbose)
            return (fieldnames, fieldtypes, header_line_no)

    def guessPrimaryKey(self, filename, sheetname, header_line_no=0, nodata=["", "Na", "NaN", "-", "--", "N/A"]):
        """
        guessPrimaryKey - make a read-pass to detect primary keys
        """
        with xlrd.open_workbook(filename) as wb:
            candidate = []
            sheet = wb.sheet_by_name(sheetname)
            cellMatrix = self.excel2Numpy(sheet)
            vMatrix = np.empty_like(cellMatrix)
            m, n = vMatrix.shape if len(vMatrix.shape) == 2 else (0, 0)
            if m == 0:
                return candidate
            for i in range(m):
                vMatrix[i, :] = xlsvalue(cellMatrix[i, :], nodata)

            # remove header lines
            vMatrix = vMatrix[header_line_no + 1:,:]


            for j in range(n):
                column = vMatrix[:, j]
                vDistinct = np.unique(column)
                # check distinct values and null
                if len(vDistinct) == len(column):
                    findnone = False
                    for jj in range(len(vDistinct)):
                        if vDistinct[jj] is None:
                            findnone = True
                            break
                    if not findnone:
                        candidate += [j]

            return candidate

    def importXls(self, filename, sheetnames="",
                  tablename=None,  #unused
                  primarykeys="",
                  guess_primary_key=True,
                  append=False,
                  Temp=False,
                  nodata=["", "Na", "NaN", "-", "--", "---", "N/A"],
                  verbose=False):
        """
        importXls
        """

        data = []
        cellMatrix = []
        sheetnames = [item.lower() for item in listify(sheetnames)]

        with xlrd.open_workbook(filename) as wb:
            for sheet in wb.sheets():
                if len(sheetnames) == 0 or lower(sheet.name) in sheetnames:
                    tablename = sheet.name
                    (fieldnames, fieldtypes, header_line_no,) = self.createTableFromXls(filename, tablename,
                                                                                        append=append,
                                                                                        primarykeys=primarykeys,
                                                                                        guess_primary_key=True,
                                                                                        Temp=Temp,
                                                                                        nodata=nodata,
                                                                                        verbose=verbose)

                    if fieldnames:
                        cellMatrix = self.excel2Numpy(sheet)
                        m, n = cellMatrix.shape if len(cellMatrix.shape) == 2 else (0, 0)
                        for i in range(header_line_no + 1, m):
                            data.append(xlsvalue(cellMatrix[i][:], nodata))

                        self.insertMany(tablename, data, verbose=verbose)

    def From(filename, sheetnames=None, nodata=["", "Na", "NaN", "-", "--", "---", "N/A"], guess_primary_key=True,
             verbose=False):
        """
        Initialize db from filename or sql
        """
        if isfiletype(filename, "db,sqlite"):
            return SqliteDB(filename)

        elif isfiletype(filename, "xls,xlsx,csv,txt,dat", check_if_exists=True):
            dsn = forceext(filename, "sqlite") if verbose else ":memory:"
            db = SqliteDB(dsn)
            db.importFrom(filename, sheetnames=sheetnames, Temp=False, nodata=nodata)
            return db

        elif isfile(forceext(filename, "sqlite")):
            db = SqliteDB(forceext(filename, "sqlite"))
            return db

        elif isquery(filename):
            # get from a simple sql string
            filexls, sheetname = SqliteDB.GetTablenameFromQuery(filename)
            if isfilexls(filexls,True):
                db = SqliteDB(forceext(filexls, "sqlite"))
                db.importFrom(filexls, sheetnames=sheetname, Temp=False, nodata=nodata)
                return db
            elif isfile(forceext(filexls, "sqlite")):
                db = SqliteDB(forceext(filexls, "sqlite"))
                return db

        return None

    From = staticmethod(From)

    def QuickTest(dsn=":memory:"):
        """
        QuickTest
        """
        db = SqliteDB(dsn)
        env = {"tablename": "test"}
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS [{tablename}](id INT,descr TEXT,[style-descr] TEXT, PRIMARY KEY(id));
            INSERT INTO [{tablename}] VALUES (1,'hello world','font: bold True;alignment: vertical top,wrap true;');
            INSERT INTO [{tablename}] VALUES (2,'hello world','font: italic true;pattern: pattern solid, fore_colour green;');
            INSERT INTO [{tablename}] VALUES (3,'hello world',NULL);
            INSERT INTO [{tablename}] VALUES (4,'hello world', 'pattern: pattern solid, fore_colour green;');
            INSERT INTO [{tablename}] VALUES (5,'hello world','font: italic true, color blue');
            """, env)
        return db

    QuickTest = staticmethod(QuickTest)

if __name__ == "__main__":
    chdir(r"D:\Users\vlr20\Projects\BitBucket\MeteoFill")
    __PROJECTDIR__ = r'D:\Users\vlr20\Projects\BitBucket\OpenSITUA\projects\project88'
    chdir(__PROJECTDIR__)
    sql = """PRAGMA TABLE_INFO([riskrecombination].[Periods]);"""
    print SqliteDB.From(sql)

