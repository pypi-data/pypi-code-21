"""
Connects to /commerce endpoints.
"""

from .gw2connector import GW2Connector
from ..gw2api import ENDPOINTS


class Commerce(GW2Connector):

    def __init__(self, apikey):
        super(Commerce, self).__init__(ENDPOINTS.COMMERCE, apikey)

    def find(self, ids, aggregate=True):
        if aggregate:
            path = '/prices'
        else:
            path = '/listings'
        params = {'ids': ','.join(str(i) for i in ids)}
        r = self._get(params=params, append_path=path)
        return r.json()
