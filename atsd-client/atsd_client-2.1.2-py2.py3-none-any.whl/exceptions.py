# -*- coding: utf-8 -*-

"""
Copyright 2017 Axibase Corporation or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License").
You may not use this file except in compliance with the License.
A copy of the License is located at

https://www.axibase.com/atsd/axibase-apache-2.0.pdf

or in the "license" file accompanying this file. This file is distributed
on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
express or implied. See the License for the specific language governing
permissions and limitations under the License.
"""


class DataParseException(Exception):
    def __init__(self, field, clazz, msg=''):
        self.msg = msg
        self.non_parsed_field = field
        self.clazz = clazz

    def __str__(self):
        return 'Data format of class ' + repr(self.clazz) \
               + ' does not match property: ' + repr(self.non_parsed_field) \
               + ', message: ' + repr(self.msg)


class ServerException(Exception):
    def __init__(self, status_code, content, msg=''):
        self.status_code = status_code
        self.content = content
        self.msg = msg

    def __str__(self):
        return ' status_code: ' + repr(self.status_code) \
               + ', content: ' + repr(self.content) \
               + ', message: ' + repr(self.msg)

class SQLException(ServerException):
    def __init__(self, status_code, content, query=''):
        super(SQLException, self).__init__(status_code, SQLException.extract_reason(content),
                                           'Unable to perform SQL query: ' + query)

    @classmethod
    def extract_reason(cls, content):
        import json
        return json.loads(content[1:])['errors'][0]['message']
