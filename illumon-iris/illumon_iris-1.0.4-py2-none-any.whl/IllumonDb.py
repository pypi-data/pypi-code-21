#
# Copyright (c) 2016-2017 Illumon and Patent Pending
#

import logging
import pandas as pd
import jpy
import random
from .java_to_python import java_type_map
from .python_to_java import python_type_map

class IllumonDb:
    """
    IllumonDb session.
    """

    def __init__(self):
        """Create a new Iris session."""
        DbGroovySession = jpy.get_type('com.illumon.integrations.common.IrisIntegrationGroovySession')
        self.session = DbGroovySession("Python Session", True)

    def reconnect(self):
        """Disconnect and then reconnect the session.  Iris state will be lost."""
        DbGroovySession = jpy.get_type('com.illumon.integrations.common.IrisIntegrationGroovySession')
        self.session.getDb().shutdown()
        self.session = DbGroovySession("Python Session", True)

    def db(self):
        """Gets an Iris database object."""
        return self.session.getDb()

    def execute(self, groovy):
        """Execute Iris groovy code."""
        self.session.execute(groovy)

    def executeFile(self, file):
        """Execute Iris groovy code contained in a file."""
        self.executeFile(file)

    def get(self, variable):
        """Gets a variable from the groovy session.

        variable -- variable name
        """
        return self.session.getVariable(variable)

    def __getitem__(self, variable):
        """Gets a variable from the groovy session.

        variable -- variable name
        """
        return self.get(variable)

    def get_df(self, variable):
        """Gets a Pandas dataframe from the groovy session.

        variable -- variable name
        """
        try:
            xrange
        except NameError:
            xrange = range

        x = random.sample(xrange(100), 3)
        table_name = "__FROZEN_TABLE%s%s%s" % (x[0], x[1], x[2])
        self.execute("%s = %s.isLive() ? db.makeRemote(emptyTable(0)).snapshot(%s,true) : %s" % (
            table_name, variable, variable, variable))
        t = self.get(table_name)
        self.execute('%s = null' % table_name)
        self.execute("""binding.variables.remove '%s'""" % table_name)

        d = {}
        col_names = []

        index = t.getIndex()
        col_defs = t.getDefinition().getColumns()
        iterator_type = jpy.get_type("java.util.PrimitiveIterator$OfLong")

        for col_def in col_defs:
            col_name = col_def.getName()
            col_type = col_def.getDataType().toString()
            logging.info("Column %s get.....; Type=%s" % (col_name, col_type))

            parser_name = col_type if (col_type in java_type_map) else "object"
            parse_func = java_type_map[parser_name]
            data = parse_func(index, t.getColumnSource(col_name), iterator_type)
            d[col_name] = pd.Series(data)
            col_names += [col_name]

            logging.info(".....Column %s get done." % col_name)

        return pd.DataFrame(d, columns=col_names)

    def push_df(self, name, df):
        """Pushes a Pandas dataframe to the Iris groovy session.

        name -- variable name for the dataframe in the groovy session
        df -- Pandas dataframe
        """

        col_names = []
        col_data = []

        for col_name in df.columns:
            col = df[col_name]
            col_type = col.dtype
            col_type_str = str(col_type)

            if col_type_str in python_type_map:
                logging.info("Column %s encoding.....; Type=%s" % (col_name, col_type_str))
                jtype, jnull, encoder = python_type_map[col_type_str]
                a = encoder(col, jtype)
                col_names += [col_name]
                col_data += [a]
                logging.info(".....Column %s encoding done." % (col_name))
            else:
                msg = "Column %s encoding unsupported.....; TypeString=%s Type=%s" % (col_name, col_type_str, col_type)
                logging.error(msg)
                raise Exception(msg)

        col_names_j = jpy.array("java.lang.String", len(col_names))
        col_data_j = jpy.array("java.lang.Object", len(col_data))

        for i in range(len(col_names)):
            col_names_j[i] = col_names[i]
            col_data_j[i] = col_data[i]

        logging.info("Dataframe %s push..." % name)
        nrows = len(df.index)
        self.session.pushDataFrame(name, nrows, col_names_j, col_data_j)
        logging.info("...Dataframe %s push done." % name)
