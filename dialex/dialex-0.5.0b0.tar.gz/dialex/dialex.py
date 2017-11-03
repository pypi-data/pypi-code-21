# -*- coding: utf-8 -*-
"""
Copyright (c) 2017 HyperLab Solutions Sdn Bhd
https://www.hyperlab.xyz/

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import requests

class Dialex(object):
    """
    Entry point for Dialex class
    """

    def __init__(self, key):
        """
        Dialex SDK Initialisation

        @param key Valid API key to use with the service
        """
        self.key = key
        self.url = 'https://dialexherok.herokuapp.com'

    def transform(self, data, lang):
        """
        Transform

        @param data The string you want to process
        @param lang Language of given input, 'en' for English, 'ms' for Malay
        """
        query = {'apikey': self.key, 'data': data, 'lang': lang}
        res = requests.get(self.url + '/api/v1/process', params=query)

        if res.status_code == 200:
            resp = res.json()
            if resp is not None:
                return resp.get('output').get('result')
            raise Exception('Empty response')
        else:
            err = res.json()
            raise Exception(err.get('message'))
