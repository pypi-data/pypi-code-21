import trust
import json


class CompleteFormatter():
    def __init__(self, finder):
        self._finder = finder

    def process(self, query, credentials, optional=False):
        self._finder.access_as(credentials)
        result = self._finder.find(query, optional=optional)
        return json.dumps(result, sort_keys=True)

    def reject_invalid(self):
        raise trust.InvalidQueryException
