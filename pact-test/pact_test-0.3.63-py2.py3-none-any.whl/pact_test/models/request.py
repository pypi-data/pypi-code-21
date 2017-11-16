class PactRequest(object):
    def __init__(self, method='', body={}, headers=[], path='', query=''):
        print('BODY??? >>> ' + str(body))
        self.body = body
        print('BODY??? >>> ' + str(self.body))
        self.path = path
        self.query = query
        self.method = method
        self.headers = headers

    def __str__(self):
        return "$$$ BODY: " + str(self.body) + ", HEADERS: " + str(self.headers)

    def stocazzo(self):
        return {
            'body': self.body
        }
