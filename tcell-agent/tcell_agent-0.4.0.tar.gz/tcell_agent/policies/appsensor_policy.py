# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved
import json
import logging

from tcell_agent.appsensor.injections_reporter import report_and_log
from tcell_agent.appsensor.sensors.database_sensor import DatabaseSensor
from tcell_agent.appsensor.sensors.misc_sensor import MiscSensor
from tcell_agent.instrumentation import safe_wrap_function
from tcell_agent.policies import TCellPolicy
from tcell_agent.rust.whisperer import init_appfirewall, apply_appfirewall, free_appfirewall
from tcell_agent.rust.request_response import create_request_response


LOGGER = logging.getLogger('tcell_agent').getChild(__name__)


class AppSensorPolicy(TCellPolicy):
    api_identifier = "appsensor"

    def __init__(self, policy_json=None):
        super(AppSensorPolicy, self).__init__()
        self.appfirewall_ptr = None
        self.init_variables()

        if policy_json is not None:
            self.load_from_json(policy_json)

    def init_variables(self):
        self.appfirewall_enabled = False
        self.misc_sensor = MiscSensor()
        self.database_sensor = DatabaseSensor()

        if self.appfirewall_ptr:
            free_appfirewall(self.appfirewall_ptr)

        self.appfirewall_ptr = None

    def process_appsensor_meta(self, appsensor_meta):
        if not self.appfirewall_enabled:
            return

        if self.appfirewall_ptr:
            request_response = create_request_response(appsensor_meta=appsensor_meta)
            whisper = apply_appfirewall(self.appfirewall_ptr, json.dumps(request_response))
            report_and_log(whisper.get("apply_response"))

    def should_check_db_rows(self, route_id):
        return self.database_sensor.should_check(route_id)

    def check_db_rows(self, appsensor_meta, number_of_records):
        safe_wrap_function(
            "Appsensor Check Number of DB Rows",
            self.database_sensor.check,
            appsensor_meta,
            number_of_records
        )

    def csrf_rejected(self, appsensor_meta):
        safe_wrap_function(
            "CSRF Exception processing",
            self.misc_sensor.csrf_rejected,
            appsensor_meta)

    def sql_exception_detected(self, appsensor_meta, exc_type_name, traceback):
        safe_wrap_function(
            "SQL Exception processing",
            self.misc_sensor.sql_exception_detected,
            appsensor_meta,
            exc_type_name,
            traceback)

    def load_from_json(self, policy_json):
        self.init_variables()

        policy_data = policy_json.get("data", {})

        if "version" in policy_json and policy_json["version"] == 2:
            sensors_json = policy_data.get("sensors")

            if sensors_json:
                options = policy_data.get("options", {})
                collect_full_uri = options.get("uri_options", {}).get("collect_full_uri", False)

                self.misc_sensor = MiscSensor(collect_full_uri=collect_full_uri,
                                              sensors_json=sensors_json)
                self.database_sensor = DatabaseSensor(collect_full_uri=collect_full_uri,
                                                      sensors_json=sensors_json)

        whisper = init_appfirewall(json.dumps(policy_json))
        if whisper.get("error"):
            LOGGER.error("Error initializing AppFirewall Policy: {e}".format(e=whisper.get("error")))
            return

        self.appfirewall_ptr = whisper.get("policy_ptr")
        self.appfirewall_enabled = whisper.get("enabled")
