# -*- coding: utf-8 -*-
"""TODO: doc module"""

from qatestlink.core.xmls.XmlParserBase import XmlParserBase

class XmlResponse(XmlParserBase):
    """TODO: doc class"""

    logged = False

    def __init__(self, xml_path=None, xml_str=None, method_name=None):
        """TODO: doc method"""
        super(XmlResponse, self).__init__(xml_path=xml_path, xml_str=xml_str)
        if method_name is None:
            raise Exception(
                'Can\'t parse XmlRequest if method_name it\'s None')
        self.method_name = method_name
        self.parse_response()

    def parse_response(self):
        """TODO: doc method"""
        if self.find_node('methodResponse') is None:
            raise Exception('Bad Response, not <methodResponse> node')
        # POST : tl.checkDevKey
        if self.method_name == 'tl.checkDevKey':
            node = self.find_node('boolean')
            if node is not None:
                self.logged = bool(node.text)
