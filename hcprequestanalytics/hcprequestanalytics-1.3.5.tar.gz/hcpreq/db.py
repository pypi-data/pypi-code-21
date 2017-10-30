# The MIT License (MIT)
#
# Copyright (c) 2017 Thorsten Simons (sw@snomis.de)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
import sqlite3
from os import cpu_count
from os.path import join, dirname
from time import time, asctime, mktime, strptime
from datetime import datetime
from collections import OrderedDict
from concurrent.futures import ProcessPoolExecutor, as_completed, TimeoutError
from tempfile import NamedTemporaryFile
from setproctitle import setproctitle

from hcpreq.queries import Queries
from hcpreq.xlsx import Csv, Xlsx


class DB():

    def __init__(self, db):
        """
        Initialize the DB handler class.

        :param db:  the database file
        """
        self.db = db

    def opendb(self):
        """
        Open the database
        """

        self.con = sqlite3.connect(self.db)
        self.con.row_factory = sqlite3.Row

    def checkdb(self):
        """
        Check if the database file exists and create it if it doesn't.

        :raises:    in case of an invalid DB
        """

        cur = self.con.execute("SELECT count(name) FROM sqlite_master "
                         "WHERE type='table' AND name='admin'")
        rec = cur.fetchone()

        # create the DB if it doesn't exist
        if not rec['count(name)']:
            self._mkdb()

        cur = self.con.execute('SELECT * FROM admin LIMIT 1')
        rec = cur.fetchone()
        if rec:
            if rec['magic'] != 'hcprequestanalytics':
                raise sqlite3.DatabaseError(
                    'not a valid hcprequestanalytics database')
        else:
            raise sqlite3.DatabaseError('not a valid hcprequestanalytics'
                                        'database')

    def listqueries(self):
        """
        Return a list of available queries.

        :return: a list of tuples (queryname, description)
        """

        return [(x, self.queries.c.get(x, 'comment')) for x in
                self.queries.c.keys() if x != 'DEFAULT']

    def _mkdb(self):
        """
        Setup a new database.
        """

        self.con.execute("CREATE TABLE admin (magic TEXT,"
                         "                    creationdate TEXT,"
                         "                    start FLOAT,"
                         "                    end FLOAT)")
        self.con.commit()

        self.con.execute("CREATE TABLE logrecs (node TEXT,\n"
                         "                      clientip TEXT,\n"
                         "                      user TEXT,\n"
                         "                      timestamp FLOAT,\n"
                         "                      timestampstr TEXT,\n"
                         "                      request TEXT,\n"
                         "                      path TEXT,\n"
                         "                      httpcode INT,\n"
                         "                      size INT,\n"
                         "                      namespace TEXT,\n"
                         "                      latency INT)")
        self.con.commit()

        self.con.execute("INSERT INTO admin (magic, creationdate, start, end)"
                         "       VALUES ('hcprequestanalytics', ?,"
                         "               99999999999.9, 0.0)",
                         (asctime(),))
        self.con.commit()



    def loaddb(self, inhdl, node):
        """
        Load the database with the records from a single file

        :param inhdl:   a filehandle for an open accesslog file
        :return:        the no. of read records
        """

        # Example records (authenticated / default namespace via www...(?)):
        # 0             1 2            3                     4      5        6                       7         8   9 10        11
        # 10.46.165.130 - webfarm_PROD [16/Aug/2017:23:03:09 +0200] "PUT     /rest/7/5/file          HTTP/1.1" 201 0 GEDP.saez 113
        # 10.49.253.207 - -            [12/Sep/2017:08:03:39 +0200] "OPTIONS /fcfs_data/Symantec_EV/ HTTP/1.1" 403 0 0

        cur = self.con.cursor()
        cur.execute("SELECT * from admin")
        _admin = row2dict(cur.fetchone())

        count = 0
        for l in inhdl.readlines():
            rec = l.strip().split()
            try:
                # attention: record with OPTIONS are different!
                # ['10.49.253.207', '-', '-', '[12/Sep/2017:08:03:39', '+0200]', '"OPTIONS', '/fcfs_data/Symantec_EV/', 'HTTP/1.1"', '403', '0', '0']
                if len(rec) == 11:
                    rec.insert(10, 'Default.Default')
                _ts = rec[3][1:] + rec[4][:-1]
                _tsnum = mktime(strptime(_ts,'%d/%b/%Y:%H:%M:%S%z'))
                _r = {'node': node,
                      'clientip': rec[0],
                      'user': rec[2],
                      'timestamp': _tsnum,
                      'timestampstr': _ts,
                      'request': rec[5][1:],
                      'path': rec[6],
                      'httpcode': int(rec[8]),
                      'size': rec[9],
                      'namespace': rec[10],
                      'latency': int(rec[11])
                      }
                _admin['start'] = _tsnum if _tsnum < _admin['start'] else _admin['start']
                _admin['end'] = _tsnum if _tsnum > _admin['end'] else _admin['end']
            except IndexError as e:
                print('IndexError on {} \n\t- {}'.format(rec, e))
                continue
            count += 1

            cur.execute('INSERT INTO logrecs'
                        '       (node, clientip, user, timestamp, timestampstr,'
                        '        request, path, httpcode, size, namespace, '
                        '        latency) VALUES'
                        '       (:node, :clientip, :user, :timestamp,'
                        '        :timestampstr, :request, :path, :httpcode,'
                        '        :size, :namespace, :latency)',
                        _r)

        self.con.commit()
        cur.execute('UPDATE admin SET start = :start, end = :end', _admin)
        self.con.commit()

        return count

    def gettimestamps(self):
        """
        Get the timestamps of the first and last entry in the database.
        """
        cur = self.con.execute("SELECT start, end from admin")
        _admin = cur.fetchone()
        return _admin['start'], _admin['end']

    def loadqueries(self, aq=None):
        """
        Load the built-in (and evetually, additional queries)
        :param aq: the name of a file containing additional queries
        """
        # make sure we find our standard queries even when frozen
        if getattr(sys, 'frozen', False):
            _stdq = join(sys._MEIPASS, 'hcpreq/queries')
        else:
            _stdq = join(dirname(__file__), 'queries')

        if aq:
            _files = [_stdq, aq]
        else:
            _files = _stdq

        self.queries = Queries(_files)

    def mpanalyze(self, prefix, queries=None, csvtype=False, processes=None):
        """
        Analyze the database, using multi-processing

        :param prefix:      the prefix to add to each csv file written
        :param queries:     a list of queries to run, or None to run all
        :param csvtype:     True if CSV files are wanted, else XLSX
        :param processes:   the number of subprocesses to use
        """
        _csv = Csv(prefix) if csvtype else Xlsx(prefix)

        with ProcessPoolExecutor(max_workers=processes) as executor:
            # create a list of all the queries to run
            qlist = []

            if queries:
                for _q in queries:
                    if not _q.endswith('*'):
                        if _q in self.queries.c.keys():
                            qlist.append(_q)
                        else:
                            print('warning: {} unavailable'.format(_q))
                    else:
                        for _c in self.queries.c.keys():
                            if _c.startswith(_q[:-1]):
                                if _c not in qlist:
                                    qlist.append(_c)
            else:
                for qs in sorted(self.queries.c.keys()):
                    # filter out the unwanted queries
                    if not qs == 'DEFAULT':
                        qlist.append(qs)

            # submit the selected queries to the ProcessPoolExecutor
            print('scheduling these queries for analytics using {} parallel '
                  'process(es):'
                  .format(processes or cpu_count()))
            mps = {}
            for q in qlist:
                print('\t{:30}: {}'.format(q, self.queries.c.get(q, 'comment')))
                mps[executor.submit(runquery, self.db, q,
                                    self.queries.c.get(q, 'query'))] = q

            # wait for the queries to be done,
            # write output for each one finished
            print('wait for queries finishing:')
            for fu in as_completed(mps):
                try:
                    runtime, data = fu.result()
                except Exception as e:
                    print('\t{} generated an exception: {}'.format(mps[fu], e),
                          flush=True)
                else:
                    print('\t{:30}: {}'.format(mps[fu], mktimestr(runtime)),
                          flush=True)
                    first = True
                    for rec in data:
                        if first:
                            _csv.newsheet(mps[fu], list(rec.keys()),
                                          runtime=mktimestr(runtime),
                                          comment=self.queries.c.get(mps[fu],
                                                                     'comment',
                                                                     fallback=''))
                            first = False
                        _csv.writerow(row2dict(rec))

                    _csv.closesheet(self.queries.c.get(mps[fu], 'freeze pane',
                                                       fallback=''))

        _start, _end = self.gettimestamps()
        _csv.close(start=_start, end=_end)

    def close(self):
        """
        Close the database.
        """
        self.con.close()

def row2dict(_r):
    """
    Convert a sqlite3.RowFactory object into a dict.

    :param _r:  sqlite3.RowFactory object
    :return:    a dict w/ the content of _r
    """
    _d = OrderedDict()
    for k in _r.keys():
        _d[k] = _r[k]
    return _d

def runquery(db, qtitle, query):
    """
    Run a single query against the database.

    :param db:      the database file's name
    :param qtitle:  the query's title
    :param query:   the query
    :return:        a list of sqlite3.Row objects
    """
    setproctitle('hcprequestanalytics query worker')

    # just open this temporary file to be able to identify which query a
    # subprocess is running ;-)
    with NamedTemporaryFile('w', prefix='I_am__*'+qtitle+'*__') as tmphdl:
        _st = datetime.today()
        con = sqlite3.connect(db)
        con.row_factory = sqlite3.Row
        con.create_aggregate("percentile", 2, PercentileFunc)
        con.create_function("tp", 2, tpfunc)
        cur = con.cursor()

        cur.execute(query)

        data = [row2dict(rec) for rec in cur.fetchall()]
        con.close()
        _end = datetime.today()-_st

    return _end, data

def mktimestr(td):
    """
    Convert a timedelta() object to a string HH:MM:SS

    :param td:  a timedelta object
    :return:    the string
    """
    _h = 60*60
    _m = 60
    _s = 1

    hours = int(td.seconds / _h)
    mins  = int((td.seconds % _h) / _m)
    secs  =  int((td.seconds % _h) % _m)

    return '{}:{}:{:02}.{}'.format('{:02}'.format(hours) if hours else '__',
                                   '{:02}'.format(mins) if mins else '__',
                                   secs,
                                   (str(td.microseconds) + '000')[:3])

class PercentileFunc():
    """
    Aggregate function for use with sqlite3 - calculates a given percentile.
    """
    def __init__(self):
        self.list = []
        self.percent = None

    def step(self, value, percent):
        if value is None:
            return
        if self.percent is None:
            self.percent = percent
        if self.percent != percent:
            return
        self.list.append(value)

    def finalize(self):
        if len(self.list) == 0:
            return None
        self.list.sort()
        return self.list[
            int(round((len(self.list) - 1) * self.percent / 100.0))]

def tpfunc(size, duration):
    """
    Calculate the throughput from size and time.
    :param size:        object size
    :param duration:    the time the transfer took
    :return:            the throughput in Bytes/sec
    """
    duration = duration if duration > 0.0001 else 0.0001

    ret =  size / duration * 1000
    # print('size={} / latency={} = {} KB/sec'.format(size, duration, ret))
    return ret
