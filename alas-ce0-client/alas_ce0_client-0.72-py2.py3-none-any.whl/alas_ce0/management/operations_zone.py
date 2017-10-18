from alas_ce0.common.client_base import EntityClientBase


class OperationsZoneClient(EntityClientBase):
    entity_endpoint_base_url = '/management/operations-zones/'

    def __init__(self, country_code='cl', **kwargs):
        super(OperationsZoneClient, self).__init__(**kwargs)
        self.entity_endpoint_base_url += country_code + '/'
