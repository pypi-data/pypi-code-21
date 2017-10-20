"""
Created on 10 de jan de 2017
Abstract Response Object
@author: rinzler
"""


class Response(object):
    __status_code = 200
    __decoded = {}
    __content = {}
    __headers = {}

    def __init__(self):
        return None

    def set_status_code(self, status_code):
        self.__status_code = status_code
        return self

    def get_status_code(self):
        return self.__status_code

    def set_decoded(self, data):
        self.__decoded = data
        return self

    def get_decoded(self):
        return self.__decoded

    def set_content(self, content):
        self.__content = content
        return self

    def get_content(self):
        return self.__content

    def set_headers(self, headers):
        self.__headers = headers
        return self

    def get_headers(self):
        return self.__headers
