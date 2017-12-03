#!/usr/bin/env python

import flask
import logging
import logging.handlers
import os
import trust
import trust.audit


flaskApp = flask.Flask(__name__)

logHandler = logging.handlers.SysLogHandler(address="/dev/log")
formatter = logging.Formatter("trust-service: [%(levelname)s] %(message)s")

logHandler.setFormatter(formatter)
logHandler.setLevel(logging.INFO)
flaskApp.logger.addHandler(logHandler)
flaskApp.logger.setLevel(logging.INFO)

trust.trust_blueprint.finder = trust.FileFinder(
    data_path=os.path.join(os.path.dirname(__file__), "tests/system/data"),
    logger=flaskApp.logger,
    audit=trust.audit.AuditToSyslog("trust-service-audit"))

flaskApp.register_blueprint(trust.trust_blueprint)

flaskApp.logger.info("The application started.")

if __name__ == "__main__":
    flaskApp.run()
