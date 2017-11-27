"""
Copyright 2017 Jake Casto

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of
the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import json
import requests

class coinschedule:

    def __init__(self, key):
        self.key = key
        self.token = None

    def call(self, method, params):
        if self.token is None and not method == "authenticate":
            raise Exception("Invalid JWT token.")

        headers = {}
        headers['Content-Type'] = 'application/json'

        if not method == "authenticate":
            headers['Authentication-Info'] = self.key

        url = 'https://api.coinschedule.com/api/v1/' + str(method) + '/'

        if not method == "authenticate":
            url = url + str(self.token)

        response = requests.post(url, json.dumps(params), headers=headers)
        response = response.json()

        code = response['code']
        message = response['error']

        if not code == 200:
            raise Exception("Error " + str(code) + ": " + message)

        return response

    def authenticate(self):
        if not len(self.key) == 16:
            raise Exception("Exepected key length 16 got" + str(len(self.key)))

        data = self.call("authenticate", [])

        if not 'token' in data:
            raise Exception("Error: " + str(data['error']))

        self.token = data['token']

    def getLive(self, cat, plat):
        fields = {}

        filters = {}
        filters['cat'] = cat
        filters['plat'] = plat

        fields['filters'] = filters

        return self.call('getLive', fields)

    def getUpcoming(self, cat, plat):
        fields = {}

        filters = {}
        filters['cat'] = cat
        filters['plat'] = plat

        fields['filters'] = filters

        return self.call('getLive', fields)

    def getDetails(self, event_id, proj_id):
        fields = {}

        fields['event_id'] = event_id
        fields['proj_id'] = proj_id

        return self.call('getUpcoming', fields)