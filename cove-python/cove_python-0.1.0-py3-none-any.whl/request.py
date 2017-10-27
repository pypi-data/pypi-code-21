class Request(object):
    def __init__(self):
        # request method (GET, POST etc.)
        self.method = None

        # (multi-dict)
        self.headers = None

        self.host = None

        # full URL requested by the client
        self.uri = None

        # request path
        self.path = None

        # (multi-dict) parsed key/value pairs in the URL query string
        self.params = None

        # (multi-dict) key/value pairs in a posted form or non-JSON request
        self.form = None

        # posted raw bytes
        self.body = None

        self.client_ip = None

        self.is_json = False

        # (any) request json data
        self.json = None
