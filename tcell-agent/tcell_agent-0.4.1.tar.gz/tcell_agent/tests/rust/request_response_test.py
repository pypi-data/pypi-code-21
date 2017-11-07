import unittest
import json

from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.rust.request_response import create_request_response


class RequestResponseTest(unittest.TestCase):

    def create_request_response_test(self):
        appsensor_meta = AppSensorMeta()
        appsensor_meta.raw_remote_address = "192.168.1.1"
        appsensor_meta.method = "GET"
        appsensor_meta.path = "/some/path"
        appsensor_meta.location = "http://192.168.1.1/some/path?xss_param=<script>"
        appsensor_meta.route_id = "12345"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"
        appsensor_meta.request_content_bytes_len = 1024
        appsensor_meta.response_content_bytes_len = 2048
        appsensor_meta.get_dict = {"user": {"xss_param": "<script>"}}
        appsensor_meta.path_dict = {"xss_param": "<script>"}
        appsensor_meta.post_dict = {("already_flattened", "xss_param"): "<script>"}
        appsensor_meta.files_dict = {("already_flattened", "xss_param"): "<script>"}
        appsensor_meta.json_body_str = json.dumps({"some_container":  {"xss_param": "<script>"}})
        appsensor_meta.cookie_dict = {"xss_param": "<script>"}
        appsensor_meta.headers_dict = {"xss_param": "<script>"}
        appsensor_meta.user_agent_str = "Mozilla"

        request_response = create_request_response(appsensor_meta)

        self.assertEqual(
            request_response,
            {
                "method": "GET",
                "status_code": 200,
                "route_id": "12345",
                "path": "/some/path",
                "query_params": [[u"xss_param", [u"<script>"]]],
                "post_params": [
                    [u"xss_param", [u"<script>"]],
                    [u"xss_param", [u"<script>"]],
                    [u"xss_param", [u"<script>"]]],
                "headers": [[u"xss_param", [u"<script>"]]],
                "cookies": [[u"xss_param", [u"<script>"]]],
                "path_params": [[u"xss_param", [u"<script>"]]],
                "remote_addr": "192.168.1.1",
                "unparsed_uri": "http://192.168.1.1/some/path?xss_param=<script>",
                "session_id": "session_id",
                "user_id": "user_id",
                "user_agent": "Mozilla",
                "request_bytes_length": 1024,
                "response_bytes_length": 2048
            }
        )
