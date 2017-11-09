# ****************       BEGIN-STANDARD-COPYRIGHT      ***************
#
# Copyright (c) 2017, Spirent Communications.
#
# All rights reserved. Proprietary and confidential information of Spirent Communications.
#
#  ***************        END-STANDARD-COPYRIGHT       ***************

"""Session profile class and necessary tools."""

import re
import six
import json

from xml.etree import ElementTree

if six.PY2:
    import codecs

from .internal import ExecutionProtocol_pb2 as pb


_DEBUG = False

_RESULT_MESSAGE = {
    pb.SUCCESS: 'success',
    pb.ABORTED: 'aborted',
    pb.TIMEOUT: 'timeout',
    pb.FAILED: 'failed',
    pb.SKIPPED: 'skipped'
}

_FIRST_CAP_RE = re.compile('(.)([A-Z][a-z]+)')
_ALL_CAP_RE = re.compile('([a-z0-9])([A-Z])')
_CAP2_PLUS = re.compile('(_)(_+)')

def _to_snake_name(name):
    temp_var = _FIRST_CAP_RE.sub(r'\1_\2', name)
    res = _ALL_CAP_RE.sub(r'\1_\2', temp_var).lower()
    res = res.replace('-', '_')
    res = _CAP2_PLUS.sub(r'\1', res)
    return res

class SessionActionResponse(object):
    """ A wrapper around a session action response """
    def __init__(self, message):
        self.message = message

        # Create dummy structured data
        self._xml = ElementTree.Element('structure')
        self._json_data = None
        self._xml_data = None
        # Need to convert all structured data to structure xml document
        self._prepare_structured_data()

        self._queries = {}
        try:
            if self.message.details != None:
                self._queries = { _to_snake_name(x.name): x for x in self.message.details.aliases }
        except AttributeError:
            pass


    def _prepare_structured_data(self):
        if not hasattr(self.message, 'details') or self.message.details is None:
            return

        mapped = None
        for s in self.message.details.structuredData:
            if '*' == s.map:
                for item in s.items:
                   self._item_to_element(self._xml, item)

            else:
                if mapped is None:
                    mapped = ElementTree.SubElement(self._xml, 'mapped')

                for item in s.items:
                    if item.name == 'json':
                        self._json_data = json.loads(self.message.details.body)
                    elif item.name == 'xml':
                        try:
                            self._xml_data = ElementTree.fromstring(item.value.encode('utf-8'))
                        except ElementTree.ParseError as err:
                            print('xml response parse error:', err)

                    # every value item here is stored XML, so we need to parse it from this items
                    mapped_child = ElementTree.fromstring(item.value.encode('utf-8'))
                    mapped.append(mapped_child)

    def _item_to_element(self, root, item):
        item_element = ElementTree.SubElement(root, item.name)
        if len(item.items) > 0:
            for child_item in item.items:
                self._item_to_element(item_element, child_item)
        else:
            item_element.text = item.value
    def _result(self):
        """
            Return action response result
            May be 'success', 'failed', 'timeout', 'aborted', 'skipped'
        """
        res = _RESULT_MESSAGE[self.message.stepResult]
        if res is None:
            return 'unknown'
        return res

    def _text(self):
        """ return a text output of executed action """
        ret = None
        if hasattr(self.message, 'details') and self.message.details != None:
            if six.PY2:
                ret = codecs.encode(self.message.details.body, 'utf-8')
            else:
                ret = self.message.details.body
        if ret is None:
            return ''
        return ret

    def __str__(self):
        return self._text()

    def __repr__(self):
        return self._text()

    def _structure(self):
        """ Return structured data of response"""
        return self.message.details.structuredData

    @property
    def text(self):
        """ return a text output of executed action """
        return self._text()

    @property
    def json(self):
        """ return a json data"""
        return self._json_data

    @property
    def xml(self):
        """ return a xml data"""
        return self._xml_data

    def __getattr__(self, key):
        if key == 'text':
            return self._text()
        elif key == 'result':
            return self._result()
        elif key == 'structure':
            return self._structure()
        elif key == 'json':
            return self._json_data
        elif key == 'xml':
            return self._xml_data
        elif key == 'data':
            return self.message.details.structuredData
        else:
            ret = self[key]
            if ret != None:
                return ret
        raise AttributeError(key)

    def __getitem__(self, key):
        if key in self._queries:
            return lambda *args: self._invoke_query(key, *args)
        raise AttributeError(key)

    def _invoke_query(self, query_name, parameters=None):
        alias = self._queries[query_name]
        if alias is None:
            return None

        if _DEBUG:
            print("do query:", alias, " params: ", parameters)
        if alias.queryFormat != None:
            query = alias.queryFormat
            if not query.startswith('.//'):
                query = './/'+ query
            # Process arguments
            if parameters != None and len(alias.arguments) > 0:
                i = 0
                param_list = []
                if isinstance(parameters, list):
                    param_list = parameters

                param_list = [parameters,]
                for param in param_list:
                    query = query.replace('{'+str(i)+'}', str(param))
                    i += 1

            # fix ' = ' wrong query strings.
            query = query.replace(' =', '=')
            query = query.replace('= ', '=')

            if _DEBUG:
                print("final query:", query)
            elements = self._xml.findall(query)
            if len(elements) == 1:
                return elements[0].text
            elif len(elements) > 1:
                if isinstance(parameters, int):
                    return elements[int(parameters)].text
                else:
                    return [x.text for x in elements]

        return None

    def __dir__(self):
        """ return a list of methods available to project"""
        res = super.__dir__(self) + list(sorted(self._queries.keys()))
        return res

    def queries(self):
        """
            Return a method names that query the structured data and return values.
            Queries may be auto-generated in iTest or be defined in response maps.
        """
        res = '['
        first_time = True
        keys = sorted(self._queries.keys())
        for x in keys:
            if first_time:
                first_time = False
            else:
                res += ', '
            msg = self._queries[x]
            if len(msg.arguments) > 0:
                # print(msg)
                res += '\'' + x + '('
                first_time_child = True
                for arg in msg.arguments:
                    if first_time_child:
                        first_time_child = False
                    else:
                        res +=', '
                    res += arg.name
                res +=  ')\''
            else:
                res += '\'' + x + '\''
        res += ']'
        return res
