# -*- coding: utf-8 -*-
"""Script to run multiple odm2timeseries WOFpy Server."""
from __future__ import (absolute_import, division, print_function)

import argparse
import configparser
import os

import wof
import wof.flask
import wof.vocabularies
from wof.examples.flask.odm2.timeseries.odm2_timeseries_dao import Odm2Dao as timeseries

# Set the paths for config files here.
M_CONFIG_FILE = os.path.join(os.path.curdir, 'odm2_config_mysql.cfg')
S_CONFIG_FILE = os.path.join(os.path.curdir, 'odm2_config_sqlite.cfg')


def get_connection(conf):
    """Parses connection string from config file.
    
    :param conf: Config file path. Ex. /path/to/config/odm2_config.cfg
    :return: Connection String.
    """
    # Parse connection from config file
    config = configparser.ConfigParser()
    with open(conf, 'r') as configfile:
        config.read_file(configfile)
        connection = config['Database']['Connection_String']

    return connection

parser = argparse.ArgumentParser(description='start WOF for an ODM2 database.')
parser.add_argument('--port',
                   help='Open port for server."', default=8080, type=int)
args = parser.parse_args()

# Add the necessary DAO objects for each config
m_dao = timeseries(get_connection(M_CONFIG_FILE))
s_dao = timeseries(get_connection(S_CONFIG_FILE))

# Create the necessary WOF config from the DAO and Config File Path
m_conf = wof.core.wofConfig(m_dao, M_CONFIG_FILE)
s_conf = wof.core.wofConfig(s_dao, S_CONFIG_FILE)

app = wof.flask.create_wof_flask_multiple({m_conf, s_conf}, templates=wof._TEMPLATES)

if __name__ == '__main__':
    wof.vocabularies.update_watermlcvs()
    url = "http://127.0.0.1:" + str(args.port)
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

    app.run(host='0.0.0.0', port=args.port, threaded=True)
