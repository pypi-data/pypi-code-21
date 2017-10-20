"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""

import json
import os
import time
import urllib
from configparser import ConfigParser
from subprocess import Popen, PIPE

import gateway_helpers as helpers
from controllers import ClientInfo, MultiClientController
from command_runners import MotorClient
from base import BaseClient
from scope import ScopeClient


# Read in config file info
cfg = ConfigParser()
PATH_TO_CFG_FILE = '/etc/gradient_one.cfg'
cfg.read(PATH_TO_CFG_FILE)
COMMON_SETTINGS = cfg['common']
CLIENT_SETTINGS = cfg['client']

# Get Sentry client for logging
SENTRY_CLIENT = helpers.get_sentry()

# Set globals
SECONDS_BTW_HEALTH_UPDATES = 30
CMD_URL = helpers.BASE_URL + '/commands'
DIRPATH = os.path.dirname(os.path.realpath(__file__))
if COMMON_SETTINGS['DOMAIN'].find("localhost") == 0 or COMMON_SETTINGS['DOMAIN'].find("127.0.0.1") == 0:  # noqa
    BASE_URL = "http://" + COMMON_SETTINGS['DOMAIN']
else:
    BASE_URL = "https://" + COMMON_SETTINGS['DOMAIN']
logger = helpers.logger


def scope_client(client_info):
    """Starts the manager for getting and running configs"""
    logger.info("initializing ScopeClient in scope_client")
    client = ScopeClient(client_info=client_info)
    client.run()


def motor_client(client_info):
    """Starts the manager for getting and running configs"""
    pid_file = os.path.join(DIRPATH, 'motor_client.pid')
    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))
    client = MotorClient(client_info=client_info)
    client.run()


class HealthClient(BaseClient):

    def __init__(self, *args, **kwargs):
        super(HealthClient, self).__init__(*args, **kwargs)

    """Manages process that posts gateway health info"""

    def put_health_data(self):
        """makes PUT with the health data to server"""
        url = helpers.BASE_URL + '/gateway/health'
        instruments = helpers.get_known_connected_instruments()
        payload = {
            "name": COMMON_SETTINGS['HARDWARENAME'],
            "company": COMMON_SETTINGS['COMPANYNAME'],
            "client_version": self.get_client_version(),
            "instruments": instruments,
            "status": "Online",
            "message": "No events"
        }
        self.put(url, data=json.dumps(payload))

    def run(self, client_info):
        """Runs the health manager indefinitely"""
        while True:
            logger.info("HealthClient is alive")
            try:
                self.put_health_data()
                self.post_logfile()
                self.update_activity_file(client_info.activity_file)
            except Exception:
                logger.info("post health data exception", exc_info=True)
                SENTRY_CLIENT.captureException()
            time.sleep(SECONDS_BTW_HEALTH_UPDATES)

    def get_client_version(self, package='gradientone'):
        """Gets version by parsing pip output"""
        version = {}
        try:
            version_file = os.path.join(DIRPATH, 'version.py')
            with open(version_file) as f:
                exec(f.read(), version)
            version = version['__version__']
        except Exception as e:
            logger.warning("Unable to read version file %s" % e)
        if not version:
            version = ""
            try:
                pip_show_pkg = ['pip', 'show', package]
                output = Popen(pip_show_pkg, stdout=PIPE).communicate()[0]
                lines = output.split('\n')
                for line in lines:
                    if line.startswith("Version:"):
                        version = line.split(':')[1].strip()
            except Exception as e:
                logger.warning("Unable to read pip version %s" % e)
        return version


def health_updates(client_info):
    """Runs the manager that posts gateway health info"""
    pid_file = os.path.join(DIRPATH, 'health_updates.pid')
    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))
    client = HealthClient()
    client.run(client_info)


def special_commands(client_info):
    pid_file = os.path.join(DIRPATH, 'special_commands.pid')
    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))
    client = SpecialCommandsClient()
    client.run(client_info)


class SpecialCommandsClient(BaseClient):

    def __init__(self, *args, **kwargs):
        super(SpecialCommandsClient, self).__init__(*args, **kwargs)

    def run(self, client_info):
        while True:
            time.sleep(1)
            try:
                headers = helpers.get_headers()
                params = {'status': 'pending', 'tag': "Special"}
                response = self.get(CMD_URL, headers=headers, params=params)
                # only process response if there are commands
                if response and len(response.json()['commands']) > 0:
                    logger.debug("Processing response: " + str(response.text) +
                                 " CMD_URL " + CMD_URL)
                    self.process_response(response)
                self.update_activity_file(client_info.activity_file)
            except Exception as e:
                logger.error("Unexpected exception %s" % e, exc_info=True)

    def process_response(self, response):
        command = response.json()['commands'][0]
        logger.info("Processing Special Command: %s" % command)
        cat = command['category']
        if cat == 'UpdateConfigFile':
            if command['arg']:
                self.update_cfg(command)
            else:
                logger.warning("Unexpected arg %s" % command['arg'])
        else:
            logger.warning("Unexpected command category %s" % cat)

    def update_cfg(self, command):
        """Grabs the new config file from the server"""
        cfgfile = urllib.URLopener()
        cfgfile.retrieve(command.arg, PATH_TO_CFG_FILE)


class GatewayClient(MultiClientController):

    def __init__(self, *args, **kwargs):
        name = 'gateway_client'
        super(GatewayClient, self).__init__(name=name, *args, **kwargs)

        """Gathers the client infos to run with controller

        The targets and names are used to create ClientInfo objects used in
        the MultiClientController run() method. The keep_alive_interval
        is the seconds allowed to pass between updates to the activity file
        before the controller will restart the client process.

        Note that the MultiClientController will pass the ClientInfo object
        to the target function so that the function will have the client
        info, most importantly the activity_file that it needs to update
        periodically within the keep_alive_interval
        """
        scope_info = ClientInfo(target=scope_client, name='scope_client',
                                keep_alive_interval=1200)
        hposts_info = ClientInfo(target=health_updates, name='health_updates',
                                 keep_alive_interval=120)
        motor_info = ClientInfo(target=motor_client, name='motor_client',
                                keep_alive_interval=120)
        spec_info = ClientInfo(target=special_commands,
                               name='special_commands',
                               keep_alive_interval=120)
        client_infos = [scope_info, hposts_info, motor_info, spec_info]

        # Other clients to be run by the MultiClientController should
        # be added here. Be sure to create a ClientInfo object with
        # the appropriate target, name, keep_alive_interval, and
        # activity file. Then append the object to client_infos

        # These client_info's will specify the client processes to be started
        # when the MultiClientController method run_clients() is called
        for client_info in client_infos:
            self.clients_dict[client_info.name] = client_info
