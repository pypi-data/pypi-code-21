class PactRequest(object):
    path = ''
    query = ''
    body = None
    headers = []
    method = 'GET'

    def __init__(self, method=None, body=None, headers=None, path=None, query=None):
        print('BODY??? >>> ' + str(body))
        self.body = body or self.body
        self.path = path or self.path
        self.query = query or self.query
        self.method = method or self.method
        self.headers = headers or self.headers

    def __str__(self):
        return "BODY: " + str(self.body) + ", HEADERS: " + str(self.headers)
