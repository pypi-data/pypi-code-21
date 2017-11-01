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
from time import time
from os.path import exists, join, dirname
from setproctitle import setproctitle

from hcpreq import parseargs
from hcpreq.db import DB
from hcpreq.logs import Handler


def opendb(db, addqueries):
    """
    Open and check the database, load the queries.

    :param db:          the database file's name
    :param addqueries:  the name of a file w/ additional queries
    :return:            a database object
    """
    db = DB(db)
    db.opendb()
    db.checkdb()
    db.loadqueries(aq=addqueries)

    return db


def main():

    opts = parseargs()

    # show the known queries
    if opts.cmd == 'showqueries':
        db = opendb(':memory:', opts.additionalqueries)
        print('available queries:')
        for q, txt in sorted(db.listqueries()):
            if not opts.oneq:
                print('\t{:30}\t{}'.format(q, txt))
            else:
                print('{} '.format(q), end='')
        if opts.oneq:
                print()

    # dump the built-in queries
    if opts.cmd == 'dumpqueries':
        db = opendb(':memory:', None)
        if getattr(sys, 'frozen', False):
            _stdq = join(sys._MEIPASS, 'hcpreq/queries')
        else:
            _stdq = join(dirname(__file__), 'queries')

        with open(_stdq, 'r') as qhdl:
            for l in qhdl.readlines():
                print(l, end='')

    # load the database from an HCP log package
    elif opts.cmd == 'load':
        if not exists(opts.logpkg):
            sys.exit('fatal: log package {} not existent'.format(opts.logpkg))
        setproctitle('hcprequestanalytics is loading {}'.format(opts.logpkg))
        db = opendb(opts.db, None)

        start1 = time()
        l = Handler(opts.logpkg)
        infiles = l.unpack()
        print('unpacking {} took {:.3f} seconds'.format(opts.logpkg,
                                                        time()-start1))
        start2 = time()
        _logrecs = 0
        for infile in infiles:
            _cnt = 0
            node = infile.split('/')[-6]
            print('\treading node {} - {} '.format(node,infile), end='')
            with open(infile, 'r') as inhdl:
                _cnt = db.loaddb(inhdl, node)
            print('- {:,} records'.format(_cnt))
            _logrecs += _cnt
        print('loading database with {:,} records took {:.3f} seconds'
              .format(_logrecs, time()-start2))

        l.close()
        db.close()

    # run queries against the database
    elif opts.cmd == 'analyze':
        setproctitle('hcprequestanalytics is analyzing {}'.format(opts.db))
        db = opendb(opts.db, opts.additionalqueries)
        try:
            _st = time()
            db.mpanalyze(opts.prefix, queries=opts.queries, csvtype=opts.csv,
                         processes=opts.processes)
            print('analytics finished after {:.3f} seconds'.format(time()-_st))
        except Exception as e:
            print('analyze failed: {}'.format(e))
        db.close()

    else:
        sys.exit('use --help')





