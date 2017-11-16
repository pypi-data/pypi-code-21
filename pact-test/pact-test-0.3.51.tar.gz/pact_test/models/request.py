class PactRequest(object):
    path = ''
    query = ''
    body = None
    headers = []
    method = 'GET'

    def __init__(self, method=None, body=None, headers=None, path=None, query=None):
        print('BODY??? >>> ' + str(body))
        self.body = body or {}
        self.path = path or ''
        self.query = query or ''
        self.method = method or ''
        self.headers = headers or []

    def __str__(self):
        return "BODY: " + str(self.body) + ", HEADERS: " + str(self.headers)
