# -*- coding: utf-8 -*-
"""TODO: doc module"""

import requests
from qatestlink.core.xmls.XmlRequest import XmlRequest
from qatestlink.core.xmls.XmlResponse import XmlResponse


class TlConnectionBase(object):
    """TODO: doc class"""

    url = None
    dev_key = None

    headers = None
    #xml_path = 'configs/base_request.xml'

    def __init__(self, url=None, dev_key=None):
        """TODO: doc method"""
        if url is None:
            raise Exception('Can\'t connect to None url')
        self.url = url
        if dev_key is None:
            raise Exception('Can\'t connect with None dek_key')
        self.dev_key = dev_key
        self.headers = {'Content-Type': 'application/xml'}
        # class logic
        #self.check_dev_key()

    def post_check_dev_key(self):
        """Return: XmlResponse"""
        return self.request(xml_request=XmlRequest(
            dev_key=self.dev_key,
            method_name='tl.checkDevKey'))

    def request(self, method_type='POST', xml_request=None):
        """TODO: doc method"""
        if method_type != 'POST':
            raise Exception('HTTP verb not supported')
        # DEBUG purpose
        print("making POST to url: {}".format(self.url))
        print("headers: {}".format(self.headers))
        print("data:\n{}".format(xml_request.prettify()))
        # end DEBUG
        response = requests.post(
            url=self.url,
            data=xml_request.prettify(),
            headers=self.headers)
        # DEBUG purpose
        print("RESPONSE from url: {}".format(self.url))
        print("Testlink method: {}".format(xml_request.method_name))
        print("body:\n{}".format(response.text))
        # end DEBUG
        xml_res = XmlResponse(
            xml_str=response.text,
            method_name=xml_request.method_name)
        # DEBUG purpose
        print("Xml response parsed:\n{}".format(xml_res.xml_str))
        return xml_res
