import json
from .dns import Resolution


class Response:

    def __init__(self, response, raise_status=False, path=None):
        self._response = response
        self.text = response.text
        self.status = response.status_code
        self.path = path
        try:
            self.data = response.json()
        except:
            self.data = response.text
        if raise_status and self.status // 100 != 2:
            raise ValueError('Bad status [{}]: {!r}'.format(
                self.status, self.text)
            )
        if self.path:
            self.parse()

    def __repr__(self):
        return 'Response[{}]({!r})'.format(self.status, self._response.url)

    def pprint(self):
        print(json.dumps(self.data, indent=4))

    def parse(self):
        if self.path == '/dns/passive':
            self.results = Response.parse_dns(self.data)
        else:
            self.results = None

    @classmethod
    def parse_dns(cls, data):
        results = []
        if not isinstance(data.get('results'), list):
            return None
        for result in data['results']:
            try:
                res = Resolution(result)
                results.append(res)
            except:
                pass
        return results
