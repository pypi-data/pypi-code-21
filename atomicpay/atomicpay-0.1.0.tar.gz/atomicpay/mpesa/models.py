class MpesaResponse(object):

    def __init__(self, response):
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
