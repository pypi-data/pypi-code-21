#! /usr/bin/env python

#
# Copyright (c) 2015 Cisco Systems, Inc. and others.  All rights reserved.
#

import argparse
import logging
import sys

from magen_rest_apis.magen_app import MagenApp
# If this is being run from workspace (as main module),
# import dev/magen_env.py to add workspace package directories.

src_ver = MagenApp.app_source_version(__name__)
if src_ver:
    # noinspection PyUnresolvedReferences
    import dev.magen_env
from magen_logger.logger_config import LogDefaults, initialize_logger
from magen_utils_apis.domain_resolver import mongo_host_port, LOCAL_MONGO_LOCATOR

from ks.settings import mongo_settings
from ks.ks_server.ks_app import MagenKeyServerApp
from ks.ks_server.key_server_api import key_service_bp, key_service_bp_v3, do_set_logging_level

__author__ = "paulq@cisco.com"
__maintainer__ = "Alena Lifar"
__email__ = "alifar@cisco.com"
__copyright__ = "Copyright(c) 2017, Cisco Systems, Inc."
__version__ = "0.4.1"
__status__ = "alpha"

SERVER_PORT = 5010

logger = logging.getLogger(LogDefaults.default_log_name)


def main(args):
    #: setup parser -----------------------------------------------------------
    parser = argparse.ArgumentParser(description="Key Service",
                                     usage=("\npython3.6 ks_server.py "
                                            "--database "
                                            "--mongo-ip-port "
                                            "--log-dir"
                                            "--console-log-level"
                                            "--key-server-ip-port"
                                            "--data-dir"
                                            "--unittest"
                                            "\n\nnote:\n"
                                            "root privileges are required "))

    parser.add_argument('--database', choices=['Mongo'], default="Mongo",
                        help='Database type such as Mongo or Cassandra. Default is Mongo')

    parser.add_argument('--data-dir',
                        help='Set directory for data files',
                        default=None)

    parser.add_argument('--mongo-ip-port',
                        help='Set Mongo IP and PORT'
                             'Default is ' + LOCAL_MONGO_LOCATOR)

    parser.add_argument(
        '--log-dir',
        default=LogDefaults.default_dir,
        help='Set directory for log files.'
             'Default is %s' %
             LogDefaults.default_dir)

    parser.add_argument('--console-log-level', choices=['debug', 'info', 'error'], default='error',
                        help='Set log level for console output.'
                             'Default is %s' % 'error')

    parser.add_argument('--unittest', action='store_true',
                        help='Unit Test Mode'
                             'Default is production)')

    parser.add_argument('--test', action='store_true',
                        help='Run server in test mode. Used for unit tests'
                             'Default is to run in production mode)')

    args, _ = parser.parse_known_args(args)

    # Set Up MongoDB Connection
    mip, mport = args.mongo_ip_port.split(":") if args.mongo_ip_port else mongo_host_port()
    mongo_settings.MongoSettings(mip, int(mport))

    # Initialize Magen Logger
    initialize_logger(
        console_level=args.console_log_level,
        output_dir=args.log_dir,
        logger=logger)
    do_set_logging_level(args.console_log_level)

    logger.info("\n\n\n\n ====== STARTING KEY SERVER  ====== \n")
    logger.info("log level=%s, log dir=%s\n", args.console_log_level, args.log_dir)

    logger.debug("STARTING SERVER")

    sys.stdout.flush()

    print("\n\n\n\n ====== STARTING MAGEN KEY SERVER  ====== \n")

    magen = MagenKeyServerApp().app
    magen.register_blueprint(key_service_bp)
    magen.register_blueprint(key_service_bp_v3, url_prefix='/magen/ks/v3')

    if args.test:
        magen.run(host='0.0.0.0', port=SERVER_PORT, debug=True, use_reloader=False)
    elif args.unittest:
        pass
    else:
        magen.run(host='0.0.0.0', port=SERVER_PORT, debug=False, threaded=True)

if __name__ == "__main__":
    main(sys.argv[1:])
else:
    pass
