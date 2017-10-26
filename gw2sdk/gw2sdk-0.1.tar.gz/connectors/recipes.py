"""
Connects to the /recipe endpoints.
"""

from .gw2connector import GW2Connector
from ..gw2api import ENDPOINTS


class Recipes(GW2Connector):

    def __init__(self, apikey):
        super(Recipes, self).__init__(ENDPOINTS.RECIPES, apikey)

    def find(self, ids):
        """Returns details on the recipe"""
        param = {'ids': ','.join(str(i) for i in ids)}
        r = self._get(params=param)
        return r.json()

    def search(self, item_id):
        """Finds recipes that is used to craft the item"""
        r = self._get(params={'output': item_id}, append_path="/search")
        return r.json()

    def find_use_of(self, item_id):
        """Finds recipes that use the item as an ingredient"""
        r = self._get(params={'input': item_id}, append_path="/search")
        return r.json()
