# coding=utf-8

import unittest

from tcell_agent.sanitize.sanitize_utils import SanitizeUtils, remove_trailing_slash
from tcell_agent.config import CONFIGURATION


class SanitizerUtilsTest(unittest.TestCase):
    def old_header_test(self):
        CONFIGURATION.app_id = None
        response_info = {}
        response_info["headers"] = {"set-cookie": ["sessionToken=abc123; Expires=Wed, 09 Jun 2021 10:18:14 GMT"]}
        SanitizeUtils.sanitize_response_info(response_info)
        self.assertEqual(response_info["headers"]["set-cookie"], [
            "sessionToken=8aed87a14d7369b35600b3eb61d24e51dab0fe083749b270acb9be31603da8d6; expires=Wed, 09 Jun 2021 10:18:14 GMT"])

    def request_sanitize_test(self):
        CONFIGURATION.app_id = None
        request_info = {}
        request_info["uri"] = "/abc/def"
        request_info["headers"] = {"cookie": ["sessionToken=abc123; sessionToken2=sdfdsf"]}
        SanitizeUtils.sanitize_request_info(request_info)
        self.assertEqual(
            request_info["headers"]["cookie"],
            [
                " sessionToken=8aed87a14d7369b35600b3eb61d24e51dab0fe083749b270acb9be31603da8d6; sessionToken2=6255969f6b578c815cc57426ad8520f5480eff23bb9f632720a38d2b2c9429aa"])

    def strip_uri_test(self):
        CONFIGURATION.app_id = None
        self.assertEqual(SanitizeUtils.strip_uri("/abc/def?bbb=abcd"), "/abc/def?bbb=")
        self.assertEqual(SanitizeUtils.strip_uri("https://aaa:8000/abc/def?bbb=ccbc"), "https://aaa:8000/abc/def?bbb=")

    def strip_query_string_test(self):
        self.assertEqual(SanitizeUtils.strip_uri("/abc/def?%C2%B5=%C3%A9%3Cscript%3E%C2%B5"), "/abc/def?%C2%B5=")
        self.assertEqual(
            SanitizeUtils.strip_uri("http://192.168.99.100:3000/account/signup/?%C2%B5=%C3%A9%3Cscript%3E%C2%B5"),
            "http://192.168.99.100:3000/account/signup/?%C2%B5=")

    def strip_path_string_test(self):
        CONFIGURATION.app_id = None
        self.assertEqual(
            SanitizeUtils.strip_uri("/vulnerabilities/%C2%B5%3Cscript%3E/?bbb=ccbc"),
            "/vulnerabilities/%C2%B5%3Cscript%3E/?bbb=")
        self.assertEqual(
            SanitizeUtils.strip_uri("http://192.168.99.100:3000/vulnerabilities/%C2%B5%3Cscript%3E/?bbb=ccbc"),
            "http://192.168.99.100:3000/vulnerabilities/%C2%B5%3Cscript%3E/?bbb=")

    def none_path_slash_remove_trailing_slash_test(self):
        self.assertEqual(remove_trailing_slash(None), None)

    def empty_path_slash_remove_trailing_slash_test(self):
        self.assertEqual(remove_trailing_slash(""), "")

    def root_path_slash_remove_trailing_slash_test(self):
        self.assertEqual(remove_trailing_slash("/"), "/")

    def no_trailing_slash_remove_trailing_slash_test(self):
        self.assertEqual(remove_trailing_slash("/index"), "/index")

    def trailing_slash_remove_trailing_slash_test(self):
        self.assertEqual(remove_trailing_slash("/index/"), "/index")
