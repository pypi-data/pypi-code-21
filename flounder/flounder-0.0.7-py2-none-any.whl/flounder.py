# -*- coding:utf8 -*-
# !/usr/bin/env python

try:  # Python 3
    from http.client import HTTPSConnection
except ImportError:
    from httplib import HTTPSConnection

import csv
import uuid

from .requests import CreateRequest

import warnings

DEFAULT_VERSION = '20150910'


class Flounder(object):
    _connection_class = HTTPSConnection

    @property
    def client_access_token(self):
        """
            Client access token provided by https://daialogflow.com/

            :rtype: str or unicode
        """
        return self._client_access_token

    @client_access_token.setter
    def client_access_token(self, client_access_token):
        """
            :type client_access_token: str or unicode
        """
        self._client_access_token = client_access_token

    def __init__(self,
                 client_access_token,
                 entity_name=None,
                 entity_csv=None,
                 session_id=None):
        super(Flounder, self).__init__()
        self._client_access_token = client_access_token
        self._base_url = 'api.dialogflow.com'
        self._version = DEFAULT_VERSION

        if session_id is None:
            self._session_id = uuid.uuid4().hex
        else:
            self._session_id = session_id

    def create_request(self, entity_name, csv_path):
        entity = self.create_entity(entity_name, csv_path)
        request = CreateRequest(self.client_access_token, self._base_url,
                                self._version, entity)
        return request

    def create_entity(self, name, csv_path):
        synonyms = self.to_list(csv_path)
        tmp_list = []
        for synonym in synonyms:
            romaji = self.to_romaji(synonym)
            hiragana = self.to_hiragana(synonym)
            katakana = self.to_katakana(synonym)
            new_synonym = {
                "synonyms": [synonym, romaji, hiragana, katakana],
                "value": romaji
            }
            tmp_list.append(new_synonym)
        return {"entries": tmp_list, "name": name}

    def to_romaji(self, text):
        from pykakasi import kakasi
        kakasi = kakasi()
        kakasi.setMode('a', 'a')
        kakasi.setMode('E', 'a')
        kakasi.setMode('K', 'a')
        kakasi.setMode('H', 'a')
        kakasi.setMode('J', 'a')
        converter = kakasi.getConverter()
        return converter.do(text.decode('utf-8'))

    def to_hiragana(self, text):
        from pykakasi import kakasi
        kakasi = kakasi()
        kakasi.setMode('H', 'H')
        kakasi.setMode('E', 'H')
        kakasi.setMode('K', 'H')
        kakasi.setMode('J', 'H')
        kakasi.setMode('a', 'H')
        converter = kakasi.getConverter()
        return converter.do(text.decode('utf-8'))

    def to_katakana(self, text):
        from pykakasi import kakasi
        kakasi = kakasi()
        kakasi.setMode('K', 'K')
        kakasi.setMode('H', 'K')
        kakasi.setMode('E', 'K')
        kakasi.setMode('J', 'K')
        kakasi.setMode('a', 'K')
        converter = kakasi.getConverter()
        return converter.do(text.decode('utf-8'))

    def to_list(self, csv_path):
        tmp_list = []
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                tmp_list.append(row[0])
            return tmp_list
