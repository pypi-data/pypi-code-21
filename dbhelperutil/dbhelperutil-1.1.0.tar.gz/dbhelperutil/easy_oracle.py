# encoding: utf-8

import cx_Oracle
import logging_helper
logging = logging_helper.setup_logging()

__author__ = u'Hywel Thomas'
__copyright__ = u'Copyright (C) 2016 Hywel Thomas'


class Oracle_Query_Helper(object):


    # -----------------------------------------------------------------------

    def __init__(self,
                 connection_string):
        self.connection_string = connection_string
        self.connection_is_open = False

    # -----------------------------------------------------------------------

    def open(self,
             force = False):
        if force or self.connection_is_open is False:
            if force and self.connection_is_open:
                try:
                    self.close()
                except Exception,e:
                    logging.exception(e)
            logging.info(u'Opening new connection to {host}'.format(host = self.connection_string.split(u'@')[-1]))
            self.con = cx_Oracle.connect(self.connection_string)
            self.cur = self.con.cursor()
            self.connection_is_open = True

    # -----------------------------------------------------------------------
    def select(self,
               query,
               *args,
               **kwargs):

        logging.debug(self.connection_string)
        logging.debug(query)
        for key,value in kwargs.iteritems():
            logging.debug(key + u':' +value)

        self.open()
        return [item for item in self.cur.execute(query,
                                                  *args,
                                                  **kwargs)]

    # -----------------------------------------------------------------------

    def write_select_results_to_file(self,
                                     query,
                                     file_handle,
                                     *args,
                                     **kwargs):

        logging.debug(self.connection_string)
        logging.debug(query)
        for key,value in kwargs.iteritems():
            logging.debug(key + u':' +value)

        self.open()
        for item in self.cur.execute(query,
                                     *args,
                                     **kwargs):
            file_handle.write(item)

    # -----------------------------------------------------------------------

    def process_select_results(self,
                               query,
                               function,
                               *args,
                               **kwargs):

        logging.debug(self.connection_string)
        logging.debug(query)
        for key,value in kwargs.iteritems():
            logging.debug(key + u':' +value)

        self.open()
        for item in self.cur.execute(query,
                                     *args,
                                     **kwargs):
            function(item)

    # -----------------------------------------------------------------------

    def update(self,
               query,
               commit = True,
               *args,
               **kwargs):

        logging.debug(self.connection_string)
        logging.debug(query)
        for key,value in kwargs.iteritems():
            logging.debug(key + u':' +value)

        self.open()
        self.cur.execute(query,
                         *args,
                         **kwargs)
        if commit:
            self.commit()


    # -----------------------------------------------------------------------

    def insert(self,
               query,
               commit = True,
               *args,
               **kwargs):

        logging.debug(self.connection_string)
        logging.debug(query)
        for key,value in kwargs.iteritems():
            logging.debug(key + u':' +value)

        self.open()
        self.cur.execute(query,
                         *args,
                         **kwargs)
        if commit:
            self.commit()

    # -----------------------------------------------------------------------

    def commit(self):
        if self.connection_is_open:
            self.con.commit()

    # -----------------------------------------------------------------------

    def close(self):
        if self.connection_is_open:
            self.connection_is_open = False
            logging.info(u'Closing connection to {host}'.format(host = self.connection_string.split(u'@')[-1]))
            self.cur.close()
            self.con.close()


    # -----------------------------------------------------------------------

    def __del__(self):
        logging.debug(u'{class_name} is being deallocated.'.format(class_name = self.__class__))
        self.close()

    # -----------------------------------------------------------------------


# ---------------------------------------------------------------------------

def select(connection_string,
           query):
    con = cx_Oracle.connect(connection_string)
    cur = con.cursor()
    try:
        results = [item for item in cur.execute(query)]
    finally:
        cur.close()
        con.close()
    return results

# ---------------------------------------------------------------------------


def update(connection_string,
                        query):
    con = cx_Oracle.connect(connection_string)
    cur = con.cursor()
    try:
        cur.execute(query)
    finally:
        cur.close()
        con.close()

# ---------------------------------------------------------------------------

# Don't really need a separate function, but it'll help readability
def insert(connection_string,
           query):
    con = cx_Oracle.connect(connection_string)
    cur = con.cursor()
    try:
        cur.execute(query)
    finally:
        cur.close()
        con.close()

# ---------------------------------------------------------------------------