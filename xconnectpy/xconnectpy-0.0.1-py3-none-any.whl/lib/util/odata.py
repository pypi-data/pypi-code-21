#!/usr/bin/python

from urllib import request
import json


class OData:

    def __init__(self, service_root, context, encode_payloads, headers={'Content-Type': 'application/json'}):
        self.service_root = service_root
        self.context = context
        self.encode_payloads = encode_payloads
        self.headers = headers

    # Set request parameters
    def construct_request(self, payload, resource) -> object:
        if self.encode_payloads:
            req = request.Request(self.service_root + resource, payload.encode('utf-8'), self.headers)
        else:
            req = request.Request(self.service_root + resource, payload, self.headers)

        return req

    # Post request
    def post(self, payload, resource):
        req = self.construct_request(payload=payload, resource=resource)
        res = request.urlopen(req, context=self.context)

        return res

    # Get request
    def get(self, resource):
        res = request.urlopen(self.service_root + resource, context=self.context)

        return res
