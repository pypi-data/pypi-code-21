# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved
from future.utils import iteritems

from tcell_agent.config import CONFIGURATION


class AppSensorMeta(object):
    def __init__(self):
        self.encoding = 'utf-8'

        self.remote_address = None
        self.raw_remote_address = None
        self.method = None
        self.location = None
        self.path = None
        self.route_id = None
        self.session_id = None
        self.user_id = None

        self.get_dict = None
        self.post_dict = None
        self.cookie_dict = None
        self.headers_dict = None
        self.files_dict = None
        self.json_body_str = None
        self.request_content_bytes_len = 0
        self.user_agent_str = None

        self.path_dict = {}

        self.response_content_bytes_len = 0
        self.response_code = 200

        self.request_processed = False
        self.response_processed = False

    def set_raw_remote_address(self, raw_remote_address):
        self.raw_remote_address = raw_remote_address
        self.remote_address = raw_remote_address
        if CONFIGURATION.hipaa_safe_mode:
            self.remote_address = "hmac:{ip}".format(ip=raw_remote_address)

    def path_parameters_data(self, path_dict):
        self.path_dict = path_dict or {}

    def set_response(self, django_response_class, response):
        if self.response_processed:
            return
        self.response_processed = True

        response_content_len = 0
        try:
            if isinstance(response, django_response_class):
                response_content_len = len(response.content)
        except:
            pass

        self.response_content_bytes_len = response_content_len
        self.response_code = response.status_code


def headers_from_environ(environ):
    include = ('content-length', 'content-type')
    exclude = ('http-cookie')

    env = environ or {}

    env_low_hyphen = {header_name.lower().replace('_', '-'): header_value
                      for header_name, header_value in iteritems(env)}

    env_filtered = {header_name: header_value
                    for header_name, header_value in iteritems(env_low_hyphen)
                    if header_name.startswith('http-') or header_name in include
                    if header_name not in exclude}

    env_deprefixed = {
        header_name[5:] if header_name.startswith('http-') else header_name:
        header_value
        for header_name, header_value in iteritems(env_filtered)
    }
    return env_deprefixed
