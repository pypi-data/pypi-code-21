#!/usr/bin/python

import sys

from xconnectpy.lib.util import OData, SSL, ConfigParser, Logger


class Client:

    # Shared constructor
    def __init__(self, config_file: str):

        # Parse settings
        self.settings = ConfigParser(config_file).parse()

        # Initialize logger
        self.logger = Logger(enable_log=self.settings['enableLogging'], log_file=self.settings['logFile'])

        # Create SSL context
        try:
            self.context = SSL(ssl_tunnel=self.settings['SSLTunnel'],
                               certificates=self.settings['certificates']).context()
            self.logger.info("Successfully created connection context.")
        except Exception:
            self.logger.error("Failed to create SSL context." + sys.exc_info()[0])
            sys.exit(1)

        # Initialize oData
        try:
            self.oData = OData(service_root=self.settings['serviceRoot'], context=self.context,
                               encode_payloads=self.settings['encodePayloads'])
            self.logger.info("Successfully initialized oData client.")
        except Exception:
            self.logger.error("Failed to initialize oData client.")
            sys.exit(1)

        # Done initializing
        self.logger.info("Ready to query.")

    def get_generic(self, resource) -> object:
        try:
            response = self.oData.get(resource=resource)
            self.logger.info("Successfully executed GET.")

            return response
        except Exception:
            self.logger.error("Failed to execute GET.")

    def post_generic(self, resource, payload):
        try:
            response = self.oData.post(payload=payload, resource=resource)
            self.logger.info("Successfully executed POST.")

            return response
        except Exception:
            self.logger.error("Failed to execute POST.")

            raise Exception('Error')
