"""
Connects to the /items endpoint.
"""

from .gw2connector import GW2Connector
from ..gw2api import ENDPOINTS


class Items(GW2Connector):

    def __init__(self, apikey):
        super(Items, self).__init__(ENDPOINTS.ITEMS, apikey)

    def find(self, ids):
        """Returns details on items"""
        params = {'ids': ','.join(str(i) for i in ids)}
        r = self._get(params=params)
        return r.json()
