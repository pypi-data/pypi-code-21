"""
hudai.resources.system_event
"""
from ..helpers.resource import Resource


class SystemEventResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/system-events')
        self.resource_name = 'SystemEvent'

    def list(self, page=None):
        return self._list(page=page)

    def create(self, name=None, payload=None):
        return self._create(name=name, payload=payload)

    def fetch(self, entity_id):
        return self._fetch(entity_id)
