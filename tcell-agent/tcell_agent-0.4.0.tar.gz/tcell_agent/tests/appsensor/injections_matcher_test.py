import unittest

from collections import namedtuple
from mock import Mock

from django.utils.datastructures import MultiValueDict

from tcell_agent.appsensor.django import set_request
from tcell_agent.appsensor.injections_matcher import InjectionsMatcher
from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.appsensor.params import flatten_clean, GET_PARAM, URI_PARAM
from tcell_agent.appsensor.sensors.injection_sensor import InjectionAttempt


FakeFile = namedtuple("FakeFile", ["name"], verbose=True)
FakeRequest = namedtuple("FakeRequest", ["body", "META", "GET", "POST", "FILES", "COOKIES", "environ"], verbose=True)
FakeResponse = namedtuple("FakeResponse", ["content", "status_code"], verbose=True)


class InjectionsMatcherTest(unittest.TestCase):
    def xss_sensor_config_from_json_test(self):
        sensor_matcher_json = {
            "xss": {
                "libinjection": True,
                "exclude_cookies": False,
                "exclude_forms": False,
                "exclusions": {"generic": ["form", "cookies"]},
                "patterns": ["1", "2"]
            }
        }

        injections_matcher = InjectionsMatcher.from_json(sensor_matcher_json)

        sensors = injections_matcher.sensors

        self.assertEqual(len(sensors), 1)
        self.assertTrue(sensors[0].libinjection)
        self.assertFalse(sensors[0].exclude_cookies)
        self.assertFalse(sensors[0].exclude_forms)
        self.assertEqual(sensors[0].exclusions, {"generic": set(["form", "cookies"])})

    def no_injections_any_matches_test(self):
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"
        files_dict = MultiValueDict()

        request = FakeRequest("", {"CONTENT_LENGTH": 1024, "HTTP_USER_AGENT": "user_agent"}, {}, {}, files_dict, {}, {})
        response = FakeResponse("AA", 200)
        set_request(appsensor_meta, request)
        appsensor_meta.set_response(type(response), response)

        sensor_matcher_json = {
            "xss": {
                "libinjection": True,
                "exclude_cookies": False,
                "exclude_forms": False,
                "exclusions": {"generic": ["form", "cookies"]},
                "patterns": ["1", "2"]
            }
        }

        injections_matcher = InjectionsMatcher.from_json(sensor_matcher_json)

        self.assertFalse(injections_matcher.any_matches(appsensor_meta))

    def one_injection_any_matches_test(self):
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"
        files_dict = MultiValueDict({"avatar": [FakeFile("<script>alert()</script>")]})

        request = FakeRequest("", {"CONTENT_LENGTH": 1024, "HTTP_USER_AGENT": "user_agent"}, {}, {}, files_dict, {}, {})
        response = FakeResponse("AA", 200)
        set_request(appsensor_meta, request)
        appsensor_meta.set_response(type(response), response)

        sensor_matcher_json = {
            "xss": {
                "libinjection": True,
                "exclude_cookies": False,
                "exclude_forms": False,
                "exclusions": {"generic": ["form", "cookies"]},
                "patterns": ["1", "2"]
            }
        }

        injections_matcher = InjectionsMatcher.from_json(sensor_matcher_json)

        self.assertTrue(injections_matcher.any_matches(appsensor_meta))

    def two_injections_any_matches_test(self):
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"
        files_dict = MultiValueDict({
            "avatar": [FakeFile("<script>alert()</script>"), FakeFile("<script></script>")]
        })

        request = FakeRequest("", {"CONTENT_LENGTH": 1024, "HTTP_USER_AGENT": "user_agent"}, {}, {}, files_dict, {}, {})
        response = FakeResponse("AA", 200)
        set_request(appsensor_meta, request)
        appsensor_meta.set_response(type(response), response)

        sensor_matcher_json = {
            "xss": {
                "libinjection": True,
                "exclude_cookies": False,
                "exclude_forms": False,
                "exclusions": {"generic": ["form", "cookies"]},
                "patterns": ["1", "2"]
            }
        }

        injections_matcher = InjectionsMatcher.from_json(sensor_matcher_json)

        self.assertTrue(injections_matcher.any_matches(appsensor_meta))

    # TODO: demarcation line
    def none_json_from_json_test(self):
        injection_matcher = InjectionsMatcher.from_json(None)

        self.assertFalse(injection_matcher.enabled)
        self.assertEqual(injection_matcher.sensors, [])

    def empty_json_from_json_test(self):
        injection_matcher = InjectionsMatcher.from_json({})

        self.assertFalse(injection_matcher.enabled)
        self.assertEqual(injection_matcher.sensors, [])

    def req_size_sensor_enabled_from_json_test(self):
        sensors_json = {
            "req_size": {
                "limit": 1024,
                "exclude_routes": ["2300"]
            }
        }
        injection_matcher = InjectionsMatcher.from_json(sensors_json)

        self.assertFalse(injection_matcher.enabled)
        self.assertEqual(injection_matcher.sensors, [])

    def xss_sensor_enabled_from_json_test(self):
        sensors_json = {
            "xss": {
                "libinjection": True,
                "patterns": ["1", "2", "8"],
                "exclusions": {
                    "bob": ["*"]
                }
            }
        }
        injection_matcher = InjectionsMatcher.from_json(sensors_json)

        self.assertTrue(injection_matcher.enabled)
        self.assertEqual(len(injection_matcher.sensors), 1)

        self.assertTrue(injection_matcher.sensors[0].enabled)
        self.assertTrue(injection_matcher.sensors[0].libinjection)
        self.assertEqual(injection_matcher.sensors[0].dp, "xss")
        self.assertFalse(injection_matcher.sensors[0].exclude_headers)
        self.assertFalse(injection_matcher.sensors[0].exclude_forms)
        self.assertFalse(injection_matcher.sensors[0].exclude_cookies)
        self.assertEqual(injection_matcher.sensors[0].exclusions, {"bob": set(["*"])})
        self.assertEqual(injection_matcher.sensors[0].active_pattern_ids, set(["1", "2", "8"]))
        self.assertFalse(injection_matcher.sensors[0].v1_compatability_enabled)
        self.assertEqual(injection_matcher.sensors[0].excluded_route_ids, set())

    def no_sensors_check_param_for_injections_test(self):
        injection_matcher = InjectionsMatcher([])
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        result = injection_matcher.check_param_for_injections(
            URI_PARAM, appsensor_meta, "dirty", "<script></script>"
        )

        self.assertEqual(result, None)

    def one_sensor_check_param_for_injections_test(self):
        fake_sensor = Mock()
        fake_sensor.applicable_for_param_type.return_value = True
        fake_sensor.get_injection_attempt.return_value = InjectionAttempt(
            GET_PARAM, "xss", {"param": "dirty", "value": "<script></script>", "pattern": "1"}
        )

        injection_matcher = InjectionsMatcher([fake_sensor])
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        result = injection_matcher.check_param_for_injections(
            GET_PARAM, appsensor_meta, "dirty", "<script></script>"
        )

        self.assertIsNotNone(result.type_of_param, GET_PARAM)
        self.assertIsNotNone(result.param_name, "dirty")
        self.assertIsNotNone(result.param_value, "<script></script>")
        self.assertIsNotNone(result.pattern, 1)
        self.assertIsNotNone(result.detection_point, "xss")

    def one_param_of_each_type_each_injection_test(self):
        fake_sensor = Mock()
        fake_sensor.applicable_for_param_type.return_value = True
        fake_sensor.get_injection_attempt.return_value = None

        sensors_json = {
            "xss": {"patterns": ["1"]}
        }
        injections_matcher = InjectionsMatcher.from_json(sensors_json)
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        get_dict = {"xss_get_param": "<script>get"}
        post_dict = {"xss_post_param": "<script>post"}
        cookie_dict = {"xss_cookie_param": "<script>cookie"}
        path_parameters = {"xss_path_param": "<script>path"}
        files_dict = MultiValueDict({"xss_avatar": [FakeFile("<script>file")]})

        request = FakeRequest(
            "{\"xss_body_param\":\"<script>body\"}",
            {"CONTENT_LENGTH": 1024, "HTTP_USER_AGENT": None},
            get_dict, post_dict, files_dict, cookie_dict, {})
        set_request(appsensor_meta, request)
        appsensor_meta.path_parameters_data(path_parameters)
        appsensor_meta.post_dict = flatten_clean("utf-8", post_dict)

        injection_attempts = []
        for injection_attempt in injections_matcher.each_injection(appsensor_meta):
            injection_attempts.append(injection_attempt)

        self.assertEqual(len(injection_attempts), 6)

        self.assertEqual(injection_attempts[0].detection_point, "xss")
        self.assertEqual(injection_attempts[0].param_name, "xss_avatar")

        self.assertEqual(injection_attempts[1].detection_point, "xss")
        self.assertEqual(injection_attempts[1].param_name, "xss_path_param")

        self.assertEqual(injection_attempts[2].detection_point, "xss")
        self.assertEqual(injection_attempts[2].param_name, "xss_get_param")

        self.assertEqual(injection_attempts[3].detection_point, "xss")
        self.assertEqual(injection_attempts[3].param_name, "xss_post_param")

        self.assertEqual(injection_attempts[4].detection_point, "xss")
        self.assertEqual(injection_attempts[4].param_name, "xss_body_param")

        self.assertEqual(injection_attempts[5].detection_point, "xss")
        self.assertEqual(injection_attempts[5].param_name, "xss_cookie_param")

    def json_body_is_an_array_each_injection_test(self):
        fake_sensor = Mock()
        fake_sensor.applicable_for_param_type.return_value = True
        fake_sensor.get_injection_attempt.return_value = None

        sensors_json = {
            "xss": {"patterns": ["1"]}
        }
        injections_matcher = InjectionsMatcher.from_json(sensors_json)
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        get_dict = {}
        post_dict = {}
        cookie_dict = {}
        path_parameters = {}
        files_dict = {}

        request = FakeRequest(
            "[\"<script>ahhhh</script>\",{\"xss_body_param\":\"<script>body\"}]",
            {"CONTENT_LENGTH": 1024, "HTTP_USER_AGENT": None},
            get_dict, post_dict, files_dict, cookie_dict, {})
        set_request(appsensor_meta, request)
        appsensor_meta.path_parameters_data(path_parameters)
        appsensor_meta.post_dict = flatten_clean("utf-8", post_dict)

        injection_attempts = []
        for injection_attempt in injections_matcher.each_injection(appsensor_meta):
            injection_attempts.append(injection_attempt)

        self.assertEqual(len(injection_attempts), 2)

        sorted_injection_attempts = sorted(injection_attempts, key=lambda ia: ia.param_name)

        self.assertEqual(sorted_injection_attempts[0].detection_point, "xss")
        self.assertEqual(sorted_injection_attempts[0].param_name, "body")

        self.assertEqual(sorted_injection_attempts[1].detection_point, "xss")
        self.assertEqual(sorted_injection_attempts[1].param_name, "xss_body_param")
