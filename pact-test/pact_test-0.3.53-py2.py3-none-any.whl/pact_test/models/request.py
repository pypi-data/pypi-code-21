class PactRequest(object):
    def __init__(self, method='', body={}, headers=[], path=None, query=None):
        print('BODY??? >>> ' + str(body))
        self.body = body
        self.path = path
        self.query = query
        self.method = method
        self.headers = headers

    def __str__(self):
        return "$$$ BODY: " + str(self.body) + ", HEADERS: " + str(self.headers)
