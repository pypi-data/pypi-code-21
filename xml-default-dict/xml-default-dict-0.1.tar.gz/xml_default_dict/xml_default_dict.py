#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
#
#  Silvio Giunge <contato@kanazuchi.com>
#  Read a xml file and convert content to a defaultdict
#


import re
from xml.dom import minidom
from collections import defaultdict


class return_xml_dict(object):

    def __init__(self, xml_file):
        self.prolog_pattern = re.compile(r"((<\?xml)(.*)(\ ?\??>))(?=.)", re.I)
        self.xml_dict = defaultdict(lambda: False)
        self.doc = minidom.parse(xml_file)
        self.get_nodes = {(x.localName, x) for x in self.doc.childNodes if x.nodeType == 1}
        for i, n in self.get_nodes:
            self.xml_dict[i] = n

    def get_prolog(self):
        self.get_prolog_data = self.prolog_pattern.findall(self.doc.toxml())
        if len(self.get_prolog_data) != 0:
            self.tmp_attrs = ""
            if self.doc.version is not None:
                self.tmp_attrs = self.tmp_attrs + "version=\"{}\"".format(self.doc.version)
            if self.doc.encoding is not None:
                self.tmp_attrs = self.tmp_attrs + " encoding=\"{}\"".format(self.doc.encoding)
            if self.tmp_attrs != "":
                self.xml_dict['@prolog'] = "<?xml {} ?>".format(self.tmp_attrs)

    def return_xml_dicts(self, _child_node):
        if _child_node.hasChildNodes():
            if len(_child_node.childNodes) > 1:
                _tmp_dict = defaultdict(lambda: False)
                _tmp_node = [(x.localName, x) for x in _child_node.childNodes if x.nodeType == 1]
                _tmp_queue = []
                for i, n in _tmp_node:
                    if isinstance(_tmp_dict[i], list):
                        _tmp_dict[i].extend([n])
                    elif i in _tmp_queue:
                        _tmp_dict[i] = [_tmp_dict[i]]
                        _tmp_dict[i].extend([n])
                    else:
                        _tmp_dict[i] = n
                        _tmp_queue.append(i)
                _get_instances = [
                    x for x in _tmp_dict if not isinstance(_tmp_dict[x], (unicode, bool, defaultdict))]
                if len(_get_instances) >= 1:
                    for _idx, _get_tag in enumerate(_get_instances):
                        if isinstance(_tmp_dict[_get_tag], list):
                            _new_tmp_dict = _tmp_dict[_get_tag]
                            _tmp_dict[_get_tag] = defaultdict(lambda: False)
                            for _i, _t in enumerate(_new_tmp_dict):
                                _tmp_dict[_get_tag][_i] = self.return_xml_dicts(_t)
                                if _t.hasAttributes():
                                    _tmp_dict[_get_tag][_i]['@attrs'] = defaultdict(lambda: False)
                                    for _item in _t.attributes.items():
                                        _tmp_dict[_get_tag][_i]['@attrs'][_item[0]] = _item[1]
                        else:
                            _new_tmp_dict = _tmp_dict[_get_tag]
                            _tmp_dict[_get_tag] = self.return_xml_dicts(_tmp_dict.values()[_idx])
                            if _new_tmp_dict.hasAttributes() and isinstance(_tmp_dict[_get_tag], (defaultdict)):
                                _tmp_dict[_get_tag]['@attrs'] = defaultdict(lambda: False)
                                for _item in _new_tmp_dict.attributes.items():
                                    _tmp_dict[_get_tag]['@attrs'][_item[0]] = _item[1]
                return _tmp_dict
            else:
                return _child_node.childNodes[0].nodeValue
        else:
            return False

    def run(self):
        self.get_prolog()
        self.get_instances = [x for x in self.xml_dict if not isinstance(
            self.xml_dict[x], (str, unicode, bool, defaultdict))]
        if len(self.get_instances) >= 1:
            for _instance in self.get_instances:
                _new_tmp_dict = self.xml_dict[_instance]
                self.xml_dict[_instance] = self.return_xml_dicts(self.xml_dict[_instance])
                if _new_tmp_dict.hasAttributes():
                    self.xml_dict[_instance]['@attrs'] = defaultdict(lambda: False)
                    for _item in _new_tmp_dict.attributes.items():
                        self.xml_dict[_instance]['@attrs'][_item[0]] = _item[1]

        return self.xml_dict
