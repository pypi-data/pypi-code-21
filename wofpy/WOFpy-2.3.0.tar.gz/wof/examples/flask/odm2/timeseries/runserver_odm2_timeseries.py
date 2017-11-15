# -*- coding: utf-8 -*-

""" Runserver Script to Deploy WOFpy.

Ex. python runserver_odm2_timeseries.py --config=odm2_config_timeseries.cfg
"""
from __future__ import (absolute_import, division, print_function)

import argparse

import configparser

import wof.flask
import wof.vocabularies
from wof.examples.flask.odm2.timeseries.odm2_timeseries_dao import Odm2Dao


def get_connection(conf):
    """Get connection string from .cfg file.

    :param conf: ODM2 Config File. Ex. 'odm2_config_timeseries.cfg'
    :return: Connection String
    """
    config = configparser.ConfigParser()
    with open(conf, 'r') as configfile:
        config.read_file(configfile)
        connection = config['Database']['Connection_String']

    return connection


parser = argparse.ArgumentParser(description='start WOF for an ODM2 database.')
parser.add_argument('--config',
                    help='Configuration file',
                    default='odm2_config_timeseries.cfg')
parser.add_argument('--port',
                    help='Open port for server."',
                    default=8080,
                    type=int)
args = parser.parse_args()

dao = Odm2Dao(get_connection(args.config))
app = wof.flask.create_wof_flask_app(dao, args.config)

if __name__ == '__main__':
    wof.vocabularies.update_watermlcvs()
    app.config['DEBUG'] = True

    url = 'http://127.0.0.1:' + str(args.port)
    print('----------------------------------------------------------------')
    print('Access Service endpoints at ')
    for path in wof.site_map(app):
        print('{}{}'.format(url, path))

    print('----------------------------------------------------------------')

    app.run(host='0.0.0.0', port=args.port, threaded=True)
