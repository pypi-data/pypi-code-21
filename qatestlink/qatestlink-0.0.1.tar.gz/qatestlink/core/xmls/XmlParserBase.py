# -*- coding: utf-8 -*-
# pylint: disable=no-self-use
"""TODO: doc module"""


from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import fromstring as xml_from_str
from xml.etree.ElementTree import tostring as xml_to_str
from xml.dom import minidom


class XmlParserBase(object):
    """TODO: doc class"""

    xml_path = None
    xml_str = None
    xml = None

    def __init__(self, xml_path=None, xml_str=None):
        """
        just xml_path: read file and load xml property
        just xml_str: read text and parse to xml property
        no params: create new xml runtime on xml property
                   with base element <methodCall></methodCall>
        with all params: Exception
        """
        if xml_path is not None and xml_str is not None:
            raise Exception('Must use just one on this params')
        # create RUNTIME xml
        if xml_path is None and xml_str is None:
            self.xml = self.read()
            # end instance creation
            return
        if xml_path is None:
            if xml_str is None:
                raise Exception('can\'t parse None xml_path')
        self.xml_path = xml_path
        if xml_str is None:
            if xml_path is None:
                raise Exception('can\'t parse None xml_str')
        self.xml_str = xml_str
        # reading from params
        self.xml = self.read(
            xml_path=self.xml_path, xml_str=self.xml_str)

    def read(self, xml_path=None, xml_str=None):
        """TODO: doc method"""
        if xml_path is not None:
            return self.read_from_path(xml_path=xml_path)
        if xml_str is not None:
            return self.read_from_str(xml_str=xml_str)
        return Element('methodCall')

    def read_from_path(self, xml_path=None):
        """TODO: doc method"""
        if xml_path is None:
            raise Exception('can\'t load None xml_path')
        return ElementTree(file=xml_path)

    def read_from_str(self, xml_str=None):
        """TODO: doc method"""
        if xml_str is None:
            raise Exception('can\'t load None xml_str')
        return xml_from_str(xml_str)

    def prettify(self, xml_element=None, indent=True):
        """Return a pretty-printed XML string for the Element"""
        if xml_element is None:
            xml_element = self.xml
        rough_string = xml_to_str(xml_element, 'utf-8')
        pretty = minidom.parseString(rough_string)
        if indent:
            return pretty.toprettyxml(indent="  ")
        return pretty.toprettyxml(indent="")

    def create_node(self, tag, parent=None, add_root=False, text=None):
        """TODO: doc method"""
        msg_tmpl = "Added element='{}' to parent='{}'"
        node = Element(tag)
        if text is not None:
            node.text = text
        if add_root:
            self.xml.append(node)
            print(msg_tmpl.format(tag, self.xml.tag))
        if parent is not None:
            parent.append(node)
            print(msg_tmpl.format(tag, parent.tag))
        return node

    def find_node(self, tag):
        """TODO: doc method"""
        for node in self.xml.iter(tag=tag):
            print("Found element tag='{}'".format(tag))
            return node
