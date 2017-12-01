from os.path import abspath, dirname
from restclients_core.dao import DAO
import os


class CoDa_DAO(DAO):
    def service_name(self):
        return 'coda'

    def service_mock_paths(self):
        return [abspath(os.path.join(dirname(__file__), "resources"))]

    def _custom_headers(self, method, url, headers, body):
        custom_headers = {}

        token = self.get_service_setting('AUTH_TOKEN')
        if token is not None:
            custom_headers["Authorization"] = "Token %s" % token

        return custom_headers
