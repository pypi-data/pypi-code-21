from __future__ import (absolute_import, division, print_function)

import os, sys

import wof.flask

import logging
import wof
from wof.examples.flask.odm2.measurement.odm2_measurement_dao import Odm2Dao
#import private_config

"""
    python runserver_odm2_measurement.py
    --config=odm2_config_measurement.cfg
     --connection=example.connection

"""
#logging.basicConfig(level=logging.DEBUG)

def startServer(config='odm2_config_measurement.cfg',connection=None,
                    openPort = 8080):
    dao = Odm2Dao(connection.read())
    app = wof.flask.create_wof_flask_app(dao, config)
    app.config['DEBUG'] = True


    url = "http://127.0.0.1:" + str(openPort)
    print("----------------------------------------------------------------")
    print("Access Service endpoints at ")
    for path in wof.site_map(app):
        print("{}{}".format(url, path))

    print("----------------------------------------------------------------")

    app.run(host='0.0.0.0', port=openPort, threaded=True)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='start WOF for an ODM2 database.')
    parser.add_argument('--config',
                       help='Configuration file', default='odm2_config_measurement.cfg')
    parser.add_argument('--connection',type=argparse.FileType('r'),
        help='The name of a file containing the Connection String eg: private.connection which has:'+
            'Connection String eg: "postgresql+psycopg2://username:password/db_name"')

    parser.add_argument('--port',
                       help='Open port for server."', default=8080, type=int)
    args = parser.parse_args()
    print(args)

    startServer(config=args.config,connection=args.connection,openPort=args.port)
