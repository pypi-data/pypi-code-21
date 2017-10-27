# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals
from __future__ import print_function

import json
import socket
import uuid
import os
import os.path
import errno
import traceback
import logging
import logging.handlers

from tcell_agent.tcell_log_formatter import TCellLogFormatter

DEFAULT_CONFIG_FILENAME = "tcell_agent.config"
DEFAULT_HOME = "tcell/"


def mkdir_p(path):
    """http://stackoverflow.com/a/600612/190597 (tzot)"""
    try:
        os.makedirs(path, exist_ok=True)  # Python>3.2
    except TypeError:
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise


def get_configuration_logger(log_filename):
    new_logger = logging.getLogger("tcell_agent_configuration")
    formatter = TCellLogFormatter(
        fmt='%(asctime)s - %(name)s - [%(tcell_version)s] - %(levelname)s[%(thread_pid)s]: %(message)s')

    fh = logging.handlers.RotatingFileHandler(log_filename, maxBytes=10 * 1024 * 1024, backupCount=5)
    fh.setFormatter(formatter)

    new_logger.setLevel("INFO")
    new_logger.addHandler(fh)
    return new_logger


def filter_commentlines(json_data):
    """
    Removes full line comments from json to provide trivial support for commenting. Does not remove
    end of line comments.
    :param json_data: A json text string
    :return: json text without comments
    """
    return "\n".join(l for l in json_data.split("\n") if not l.strip().startswith("//"))


class TcellAgentConfiguration(object):
    def __init__(self, filename=DEFAULT_CONFIG_FILENAME):
        self.enabled = True
        self.allow_payloads = True

        self.max_data_ex_db_records_per_request = 1000

        self.version = 0
        self.app_id = None
        self.api_key = None
        self.tcell_api_url = "https://api.tcell.io/api/v1"
        self.tcell_input_url = "https://input.tcell.io/api/v1"
        self.company = None
        self.uuid = str(uuid.uuid4())
        self.host_identifier = None
        self.preload_policy_filename = None
        self.fetch_policies_from_tcell = True
        self.instrument_for_events = True
        self.hmac_key = None
        self.logging_options = {}
        self.reverse_proxy = True
        self.reverse_proxy_ip_address_header = None
        self.hipaa_safe_mode = False
        self.max_csp_header_bytes = None
        self.enabled_instrumentations = {"django_auth": True}
        self.event_batch_size_limit = 100
        self.event_time_limit_seconds = 15
        self.event_queue_intake_size = 200
        self.demo_mode = False

        self.js_agent_api_base_url = None
        self.js_agent_url = "https://api.tcell.io/tcellagent.min.js"
        self.startup_js_agent_url = "https://api.tcell.io/tcellagent.min.js"

        self.tcell_home = os.environ.get("TCELL_AGENT_HOME", DEFAULT_HOME)
        self.cache_folder = os.path.join(self.tcell_home, 'cache/')
        self.log_directory = os.environ.get("TCELL_AGENT_LOG_DIR", os.path.join(self.tcell_home, "logs/"))
        self.log_filename = os.path.join(self.log_directory, "tcell_agent.log")

        mkdir_p(self.tcell_home)
        mkdir_p(self.cache_folder)

        config_filename = os.path.abspath(os.environ.get("TCELL_AGENT_CONFIG", filename))
        backup_check_config_filename = os.path.abspath(os.path.join(self.tcell_home, filename))

        config_logger = None

        try:
            if os.path.isfile(config_filename) == False:
                if os.path.isfile(backup_check_config_filename) == True:
                    config_filename = backup_check_config_filename

                else:
                    mkdir_p(self.log_directory)
                    config_logger = get_configuration_logger(self.log_filename)
                    config_logger.info(
                        "Configuration file not found (checked: {c1} and {c2}), using environmental variables."
                            .format(c1=config_filename, c2=backup_check_config_filename)
                    )
                    config_filename = None

            if config_filename != None:
                if os.access(config_filename, os.R_OK) == False:
                    print("tCell.io Agent: [Error] Permission denied opening config file.")
                    mkdir_p(self.log_directory)
                    config_logger = get_configuration_logger(self.log_filename)
                    config_logger.error("Permission denied for file '{c1}'".format(c1=config_filename))

                else:
                    with open(config_filename, "r") as data_file:
                        try:
                            json_data = filter_commentlines(data_file.read())
                            config_json = json.loads(json_data)
                            self.read_config(config_json)
                        except:
                            print("tCell.io Agent: [Error] Could not parse json in config file.")
                            traceback.print_exc()

                            mkdir_p(self.log_directory)
                            config_logger = get_configuration_logger(self.log_filename)
                            config_logger.exception("Could not parse json in config file: " + config_filename + ".")
        except Exception as ex:
            print("Exception loading configuration file.")
            print(ex)
            mkdir_p(self.log_directory)
            config_logger = get_configuration_logger(self.log_filename)
            config_logger.exception("Exception loading configuration file.")
            raise

        self.config_filename = config_filename

        mkdir_p(self.log_directory)
        if config_logger is None:
            config_logger = get_configuration_logger(self.log_filename)

        self.app_firewall_payloads_log_filename = os.path.join(self.log_directory, "tcell_agent_payloads.log")
        config_logger.info("Checking configuration environmental variables.")

        self.demo_mode = os.environ.get('TCELL_DEMOMODE', self.demo_mode) in [True, "true", "1"]
        if self.demo_mode:
            self.event_batch_size_limit = 1
            self.event_time_limit_seconds = 5

        if 'TCELL_AGENT_ALLOW_UNENCRYPTED_APPSENSOR_PAYLOADS' in os.environ:
            print("tCell.io Agent: [DEPRECATED] TCELL_AGENT_ALLOW_UNENCRYPTED_APPSENSOR_PAYLOADS"
                  " is deprecated, please switch to TCELL_AGENT_ALLOW_PAYLOADS.")
            self.allow_payloads = os.environ['TCELL_AGENT_ALLOW_UNENCRYPTED_APPSENSOR_PAYLOADS'] in [True, "true", "1"]

        if 'TCELL_AGENT_ALLOW_UNENCRYPTED_APPFIREWALL_PAYLOADS' in os.environ:
            print("tCell.io Agent: [DEPRECATED] TCELL_AGENT_ALLOW_UNENCRYPTED_APPFIREWALL_PAYLOADS"
                  " is deprecated, please switch to TCELL_AGENT_ALLOW_PAYLOADS.")
            self.allow_payloads = os.environ['TCELL_AGENT_ALLOW_UNENCRYPTED_APPFIREWALL_PAYLOADS'] in [True, "true", "1"]

        if 'TCELL_AGENT_ALLOW_PAYLOADS' in os.environ:
            self.allow_payloads = os.environ['TCELL_AGENT_ALLOW_PAYLOADS'] in [True, "true", "1"]

        self.app_id = os.environ.get("TCELL_AGENT_APP_ID", self.app_id)
        self.api_key = os.environ.get("TCELL_AGENT_API_KEY", self.api_key)
        self.host_identifier = os.environ.get("TCELL_AGENT_HOST_IDENTIFIER", self.host_identifier)
        self.tcell_api_url = os.environ.get("TCELL_API_URL", self.tcell_api_url)
        self.tcell_input_url = os.environ.get("TCELL_INPUT_URL", self.tcell_input_url)
        self.hmac_key = os.environ.get("TCELL_HMAC_KEY", self.hmac_key)

        if self.app_id is None:
            config_logger.warn("tCell.io APP ID not set by file or environmental variable.")
        if self.api_key is None:
            config_logger.warn("tCell.io API Key not set by file or environmental variable.")

        if self.hipaa_safe_mode:
            if not self.hmac_key:
                print("ERROR: HIPAA safe mode enabled but HMAC KEY was not provided. Disabling Agent.")
                config_logger.error("HIPAA safe mode enabled but HMAC KEY was not provided. Disabling Agent.")
                self.app_id = None
                self.api_key = None
            if not self.tcell_input_url or "saninput" not in self.tcell_input_url:
                print(
                    "ERROR: HIPAA safe mode enabled needs to have tcell_input_url configured properly. Disabling Agent.")
                config_logger.error(
                    "HIPAA safe mode enabled needs to have tcell_input_url configured properly. Disabling Agent.")
                self.app_id = None
                self.api_key = None

    def read_config(self, config_json):
        if "version" not in config_json:
            self.version = 0
            self.company = config_json.get("COMPANY")
            self.app_id = config_json.get("APP_NAME")
            self.api_key = config_json.get("API_KEY")
            self.tcell_input_url = config_json.get("TCELL_INPUT_URL", "https://input.tcell.io:8008")
            self.host_identifier = socket.getfqdn()
        else:
            self.version = config_json["version"]
            if self.version == 1:
                applications = config_json["applications"]
                if applications and len(applications) > 0:
                    application_config_json = applications[0]  # Get the first application for now
                    v0_app_id = application_config_json.get("name")
                    self.app_id = application_config_json.get("app_id", v0_app_id)
                    self.api_key = application_config_json.get("api_key")
                    self.enabled = application_config_json.get("enabled", True)
                    self.fetch_policies_from_tcell = application_config_json.get("fetch_policies_from_tcell", True)
                    self.preload_policy_filename = application_config_json.get("preload_policy_filename")
                    self.logging_options = application_config_json.get("logging_options", self.logging_options)

                    # DEPRECATED: this was incorrectly placed here. Keep it here until we can
                    # be sure that no customers are relying on this
                    self.log_directory = self.logging_options.get("log_dir", self.log_directory)

                    self.log_directory = application_config_json.get("log_dir", self.log_directory)
                    self.log_filename = os.path.join(self.log_directory,
                                                     self.logging_options.get("filename", "tcell_agent.log"))
                    self.instrument_for_events = application_config_json.get("instrument_for_events", True)
                    new_api_url = application_config_json.get("tcell_api_url", None)
                    if (new_api_url is not None and new_api_url != self.tcell_api_url):
                        # Change default jsagent
                        self.js_agent_api_base_url = new_api_url
                        self.tcell_api_url = new_api_url

                    self.tcell_input_url = application_config_json.get("tcell_input_url", self.tcell_input_url)
                    host_identifier = application_config_json.get("host_identifier")
                    if host_identifier is None:
                        host_identifier = socket.getfqdn()
                    self.host_identifier = host_identifier

                    self.hipaa_safe_mode = application_config_json.get("hipaaSafeMode", False)
                    self.hmac_key = application_config_json.get("hmac_key", None)

                    self.js_agent_api_base_url = application_config_json.get("js_agent_api_base_url",
                                                                             self.js_agent_api_base_url)
                    self.js_agent_url = application_config_json.get("js_agent_url", self.js_agent_url)
                    self.startup_js_agent_url = self.js_agent_url

                    max_csp_header_bytes = application_config_json.get("max_csp_header_bytes", None)
                    if max_csp_header_bytes and max_csp_header_bytes > 0:
                        self.max_csp_header_bytes = max_csp_header_bytes

                    if 'allow_unencrypted_appsensor_payloads' in application_config_json:
                        self.allow_payloads = application_config_json['allow_unencrypted_appsensor_payloads']
                    if 'allow_unencrypted_appfirewall_payloads' in application_config_json:
                        self.allow_payloads = application_config_json['allow_unencrypted_appfirewall_payloads']
                    if 'allow_payloads' in application_config_json:
                        self.allow_payloads = application_config_json['allow_payloads']

                    data_exposure = application_config_json.get('data_exposure', {})
                    self.max_data_ex_db_records_per_request = data_exposure.get('max_data_ex_db_records_per_request',
                                                                                self.max_data_ex_db_records_per_request)

                    self.reverse_proxy = application_config_json.get('reverse_proxy', self.reverse_proxy)
                    self.reverse_proxy_ip_address_header = application_config_json.get(
                        'reverse_proxy_ip_address_header', self.reverse_proxy_ip_address_header)

                    self.enabled_instrumentations = application_config_json.get('enabled_instrumentations', self.enabled_instrumentations)

                    self.demo_mode = application_config_json.get('demomode', self.demo_mode)

                    # for old tcell_input_url
                    self.company = application_config_json.get("company")

    def should_instrument_django_auth(self):
        return self.enabled_instrumentations.get("django_auth", True) in [True, "true"]
