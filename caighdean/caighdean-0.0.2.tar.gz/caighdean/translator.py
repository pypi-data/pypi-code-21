# -*- coding: utf-8 -*-

import json
import requests

from nltk.tokenize.moses import MosesDetokenizer

from .exceptions import TranslationError


class Translator(object):
    service_url = "http://borel.slu.edu/cgi-bin/seirbhis3.cgi"

    def __init__(self, src_lang="gd"):
        self.src_lang = src_lang
        self.target_lang = "ga"

    def request_params(self, phrase):
        return {
            "teacs": phrase,
            "foinse": self.src_lang}

    def make_request(self, params):
        return requests.post(self.service_url, params)

    def parse_response(self, msg):
        return MosesDetokenizer().detokenize(
            [x[1] for x in json.loads(msg)],
            return_str=True).replace("\\n", "\n")

    def translate(self, phrase):
        response = self.make_request(
            self.request_params(phrase))
        if response.status_code != 200:
            raise TranslationError(
                "Unable to connect to translation service")
        return self.parse_response(response.content)
