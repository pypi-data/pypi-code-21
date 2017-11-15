from __future__ import (absolute_import, division, print_function)


import logging

from wof.examples.flask.barebones.LCM_dao import LCMDao

import wof
import wof.flask
from wof.examples.flask.csv_server.csv_dao import CsvDao
from wof.examples.flask.swis.swis_dao import SwisDao

logging.basicConfig(level=logging.DEBUG)

def startServer(openPort):
    SWIS_CONFIG='swis/swis_config.cfg'
    LCM_CONFIG='barebones/LCM_config.cfg'
    swis_dao = SwisDao('swis/swis_config.cfg',
                       database_uri='sqlite:///swis/swis2.db')
    lcm_dao = LCMDao('sqlite:///barebones/LCM_Data/LCM.db',
                         'barebones/LCM_config.cfg')
    CSV_CONFIG_FILE = 'csv_server/csv_config.cfg'
    SITES_FILE = 'csv_server/sites.csv'
    VALUES_FILE = 'csv_server/data.csv'
    csv_doa = CsvDao(SITES_FILE, VALUES_FILE)

    # swis_wof = WOF(swis_dao)
    # swis_wof.config_from_file('swis/swis_config.cfg')
    #
    # lcm_wof = WOF(lcm_dao)
    # lcm_wof.config_from_file('barebones/LCM_config.cfg')
    # #Create the Flask applications
    # swis_flask_app = create_app(swis_wof)
    # lcm_flask_app = create_app(lcm_wof)
    #
    # #Create the soaplib classes
    # SWISWOFService = create_wof_service_class(swis_wof)
    # LCMWOFService = create_wof_service_class(lcm_wof)
    #
    # #Create the soaplib applications
    # swis_soap_app = soaplib.core.Application(services=[SWISWOFService],
    #     tns='http://www.cuahsi.org/his/1.0/ws/',
    #     name='WaterOneFlow')
    #
    # lcm_soap_app = soaplib.core.Application(services=[LCMWOFService],
    #     tns='http://www.cuahsi.org/his/1.0/ws/',
    #     name='WaterOneFlow')
    #
    # #Create WSGI apps from the soaplib applications
    # swis_soap_wsgi_app = soaplib.core.server.wsgi.Application(swis_soap_app)
    # lcm_soap_wsgi_app = soaplib.core.server.wsgi.Application(lcm_soap_app)
    #
    # combined_app = DispatcherMiddleware(NotFound, {
    #     '/swis': swis_flask_app,
    #     '/lcm': lcm_flask_app,
    #     '/swis/soap/wateroneflow': swis_soap_wsgi_app,
    #     '/lcm/soap/wateroneflow': lcm_soap_wsgi_app
    # })


    conf_swis = wof.core.wofConfig(swis_dao, SWIS_CONFIG)
    conf_lcm = wof.core.wofConfig(lcm_dao, LCM_CONFIG)
    conf_csv = wof.core.wofConfig(csv_doa, CSV_CONFIG_FILE)

    app= wof.flask.create_wof_flask_multiple({conf_swis, conf_lcm, conf_csv}, templates=wof._TEMPLATES)


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
    # This must be an available port on your computer.
    # For example, if 8080 is already being used, try another port such as
    # 5000 or 8081.
    import argparse

    parser = argparse.ArgumentParser(description='start WOF multiple server example.')
    parser.add_argument('--port',
                       help='Open port for server."', default=8080, type=int)
    args = parser.parse_args()
    print(args)

    startServer(args.port)
