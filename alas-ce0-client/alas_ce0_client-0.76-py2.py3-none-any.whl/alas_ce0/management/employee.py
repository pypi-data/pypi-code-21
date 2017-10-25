from alas_ce0.common.client_base import EntityClientBase


class EmployeeClient(EntityClientBase):
    entity_endpoint_base_url = '/management/employees/'

    def __init__(self, country_code='cl', **kwargs):
        super(EmployeeClient, self).__init__(**kwargs)
        self.entity_endpoint_base_url += country_code + '/'
