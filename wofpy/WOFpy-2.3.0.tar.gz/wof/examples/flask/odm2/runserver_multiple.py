from __future__ import (absolute_import, division, print_function)

import logging
import os
import tempfile
import sys

from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.serving import run_simple
from werkzeug.exceptions import NotFound

import wof
import wof.flask
from wof.examples.flask.odm2.measurement.odm2_measurement_dao import Odm2Dao as measurement
from wof.examples.flask.odm2.timeseries.odm2_timeseries_dao import Odm2Dao as timeseries
#from measurement.private_config import odm2_connection_string

#logging.basicConfig(level=logging.DEBUG)

M_CONFIG_FILE = os.path.join('measurement', 'odm2_config_measurement.cfg')
T_CONFIG_FILE = os.path.join('timeseries', 'odm2_config_timeseries.cfg')


def startServer(m_config=M_CONFIG_FILE,
                t_config=T_CONFIG_FILE,
                m_connection=None,
                t_connection=None,
                openPort=8080):
    if m_connection is None and t_connection is None:
        sys.exit("connection  must be provided")
    m_dao = measurement(m_connection.read())
    t_dao = timeseries(t_connection.read())

    m_conf = wof.core.wofConfig(m_dao, m_config)
    t_conf = wof.core.wofConfig(t_dao, t_config)

    app= wof.flask.create_wof_flask_multiple({m_conf, t_conf}, templates=wof._TEMPLATES)

    url = "http://127.0.0.1:" + str(openPort)
    print("----------------------------------------------------------------")
    print("Service endpoints")
    for path in wof.flask.site_map_flask_wsgi_mount(app):
        print("{}{}".format(url, path))

    print("----------------------------------------------------------------")
    print("----------------------------------------------------------------")
    print("Access HTML descriptions of endpoints at ")
    for path in wof.site_map(app):
        print("{}{}".format(url, path))

    print("----------------------------------------------------------------")

    app.run(host='0.0.0.0', port=openPort, threaded=True)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='start WOF for an ODM2 database.')
    parser.add_argument('--timeseries',
                       help='Timeseries Configuration file', default=M_CONFIG_FILE)
    parser.add_argument('--measurement',
                       help='Measurement Configuration file', default=T_CONFIG_FILE)
    parser.add_argument('--timeseries_connection',type=argparse.FileType('r'),
         help='The name of a file containing the Connection String eg: private.connection which has: mysql://username:password@localhost/database')

    parser.add_argument('--measurement_connection',type=argparse.FileType('r'),
         help='The name of a file containing the Connection String eg: private.connection which has:'+
             'Connection String eg: "postgresql+psycopg2://username:password/db_name"')
    parser.add_argument('--port',
                       help='Open port for server."', default=8080, type=int)
    args = parser.parse_args()
    print(args)

    startServer( m_config=args.timeseries,
                 t_config=args.measurement,
                 m_connection=args.measurement_connection,
                 t_connection=args.timeseries_connection,
                 openPort=args.port )


