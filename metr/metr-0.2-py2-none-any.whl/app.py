import matplotlib
import re
import sys
import os
import sqlite3
from doan.dataset import Dataset
from doan.graph import plot_date
from metr.db import get_points, set_point, migrate


matplotlib.use('AGG')


DIR = '/srv/metr/'
DB = DIR + 'db/metr.db'
BASE_URL = '/metr/'
IMAGE_DIR = DIR + 'output/'


class Response(object):
    pass


def show_metric(metric):
    conn = sqlite3.connect(DB)
    points = get_points(conn, metric)
    conn.close()
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)
    fname = IMAGE_DIR + '%s.png' % metric
    d = Dataset([Dataset.DATE, Dataset.FLOAT])
    d.load(points)
    plot_date(d, output=fname, figsize=(14, 7), linestyle='-')

    data = open(fname, 'rb').read()
    r = Response()
    r.body = data
    r.code = '200 OK'
    r.headers = [('content-type', 'image/png'),
                 ('content-length', str(len(r.body)))]
    return r


def update_metric(metric, value, dt=None):
    conn = sqlite3.connect(DB)
    set_point(conn, metric, value, dt)
    conn.close()

    r = Response()
    r.body = ''
    r.code = '302 Found'
    r.headers = [('Location', '/metr/%s' % metric)]
    return r


def list_metrics():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('select name from metric')

    data = []
    rows = c.fetchall()
    for row in rows:
        data.append('<a href="%s">%s</a>' % (BASE_URL + row[0], row[0]))
    conn.close()

    r = Response()
    r.body = '<br />'.join(data).encode()
    r.code = '200 OK'
    r.headers = [('content-type', 'text/html'),
                 ('content-length', str(len(r.body)))]
    return r


def get_handler(environ):
    default = list_metrics

    routes = {
        r'^/metr/([a-z0-9\-_]{3,128})$': show_metric,
        r'^/metr/([a-z0-9\-_]{3,128})/([0-9\.]{1,16})$': update_metric,
        r'^/metr/([a-z0-9\-_]{3,128})/([0-9\.]{1,16})/([a-z0-9\-_T]{3,20})$':
        update_metric,
    }
    path_info = environ.get('PATH_INFO', '')
    for r in routes:
        match = re.match(r, path_info)
        if match:
            return routes[r], match.groups(), match.groupdict()
    return default, [], {}


def migrate_db():
    conn = sqlite3.connect(DB)
    migrate(conn)


def application(environ, start_response):

    handler, args, kwargs = get_handler(environ)
    r = handler(*args, **kwargs)
    start_response(r.code, r.headers)
    return [r.body]
