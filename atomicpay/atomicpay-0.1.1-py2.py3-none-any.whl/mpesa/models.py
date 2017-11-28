# Copyright (c) 2017 Turbopay Holdings Ltd

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE


class MpesaResponse(object):

    def __init__(self, response):
        self.status_code = response.status_code
        self.response = response.json()

    @property
    def code(self):
        if 'ResponseCode' in self.response:
            return (
                200 if self.response['ResponseCode'] == '0'
                else self.response['ResponseCode']
            )

        return self.response['errorCode']

    @property
    def text(self):
        if 'ResponseDescription' in self.response:
            return self.response['ResponseDescription']

        return self.response['errorMessage']

    def json(self):
        return self.response

    @property
    def ok(self):
        return self.code == 200

    def __str__(self):
        return "<MpesaResponse [{}] >".format(self.code)
