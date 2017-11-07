from future.utils import iteritems

from tcell_agent.appsensor import params
from tcell_agent.appsensor.params import GET_PARAM, POST_PARAM, JSON_PARAM, COOKIE_PARAM, URI_PARAM, HTTP_HEADER_PARAM
from tcell_agent.instrumentation import safe_wrap_function
from tcell_agent.appsensor.sensors.cmdi_sensor import CmdiSensor
from tcell_agent.appsensor.sensors.fpt_sensor import FptSensor
from tcell_agent.appsensor.sensors.nullbyte_sensor import NullbyteSensor
from tcell_agent.appsensor.sensors.retr_sensor import RetrSensor
from tcell_agent.appsensor.sensors.sqli_sensor import SqliSensor
from tcell_agent.appsensor.sensors.xss_sensor import XssSensor
from tcell_agent.utils.json_utils import parse_json


class InjectionsMatcher(object):
    DETECTION_POINTS_V2 = {
        "xss": XssSensor,
        "sqli": SqliSensor,
        "cmdi": CmdiSensor,
        "fpt": FptSensor,
        "nullbyte": NullbyteSensor,
        "retr": RetrSensor
    }

    def __init__(self, sensors):
        self.sensors = sensors
        self.enabled = len(sensors) > 0

    # considers no sensors as a match
    def any_matches(self, meta_data):
        if not self.enabled:
            return True

        for _ in self.each_injection(meta_data):
            return True

        return False

    def each_injection(self, appsensor_meta):
        if not self.enabled:
            return

        get_dict = params.flatten_clean(appsensor_meta.encoding, appsensor_meta.get_dict)
        cookie_dict = params.flatten_clean(appsensor_meta.encoding, appsensor_meta.cookie_dict)
        path_dict = params.flatten_clean(appsensor_meta.encoding, appsensor_meta.path_dict)
        json_body = parse_json(appsensor_meta.encoding, appsensor_meta.json_body_str)
        if json_body and isinstance(json_body, list):
            json_body = {'body': json_body}

        headers_dict = params.flatten_clean(appsensor_meta.encoding, appsensor_meta.headers_dict)
        body_dict = params.flatten_clean(appsensor_meta.encoding, json_body or {})

        post_dict = appsensor_meta.post_dict
        files_dict = appsensor_meta.files_dict

        for param_name, param_value in iteritems(files_dict):
            injection_attempt = safe_wrap_function(
                "AppSensor Check Filename injections",
                self.check_param_for_injections,
                POST_PARAM,
                appsensor_meta,
                param_name,
                param_value
            )

            if injection_attempt:
                yield injection_attempt

        for param_name, param_value in iteritems(path_dict):
            injection_attempt = safe_wrap_function(
                "AppSensor Check Path Params injections",
                self.check_param_for_injections,
                URI_PARAM,
                appsensor_meta,
                param_name,
                param_value
            )

            if injection_attempt:
                yield injection_attempt

        for param_name, param_value in iteritems(get_dict):
            injection_attempt = safe_wrap_function(
                "AppSensor Check GET var injections",
                self.check_param_for_injections,
                GET_PARAM,
                appsensor_meta,
                param_name,
                param_value
            )

            if injection_attempt:
                yield injection_attempt

        for param_name, param_value in iteritems(post_dict):
            injection_attempt = safe_wrap_function(
                "AppSensor Check POST var injections",
                self.check_param_for_injections,
                POST_PARAM,
                appsensor_meta,
                param_name,
                param_value
            )

            if injection_attempt:
                yield injection_attempt

        for param_name, param_value in iteritems(body_dict):
            injection_attempt = safe_wrap_function(
                "AppSensor Check JSON var injections",
                self.check_param_for_injections,
                JSON_PARAM,
                appsensor_meta,
                param_name,
                param_value
            )

            if injection_attempt:
                yield injection_attempt

        for param_name, param_value in iteritems(cookie_dict):
            injection_attempt = safe_wrap_function(
                "AppSensor Check COOKIE var injections",
                self.check_param_for_injections,
                COOKIE_PARAM,
                appsensor_meta,
                param_name,
                param_value
            )

            if injection_attempt:
                yield injection_attempt

        for param_name, param_value in iteritems(headers_dict):
            injection_attempt = safe_wrap_function(
                "AppSensor Check HEADERS var injections",
                self.check_param_for_injections,
                HTTP_HEADER_PARAM,
                appsensor_meta,
                param_name,
                param_value
            )

            if injection_attempt:
                yield injection_attempt

    def check_param_for_injections(self, param_type, appsensor_meta, param_name, param_value):
        param_name = param_name[-1]

        for sensor in self.sensors:
            if not sensor.applicable_for_param_type(param_type):
                continue

            injection_attempt = sensor.get_injection_attempt(param_type, appsensor_meta, param_name, param_value)
            if injection_attempt:
                return injection_attempt

        return None

    @classmethod
    def from_json(cls, sensors_json):
        sensors_json = sensors_json or {}
        sensors = []

        for sensor_key, settings in iteritems(sensors_json):

            clazz = cls.DETECTION_POINTS_V2.get(sensor_key)

            if not clazz:
                continue

            updated_settings = {"enabled": True}
            updated_settings.update(settings)
            sensors.append(clazz(updated_settings))

        return InjectionsMatcher(sensors)
