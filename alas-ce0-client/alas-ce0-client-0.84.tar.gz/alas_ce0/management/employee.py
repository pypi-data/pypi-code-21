from alas_ce0.common.client_base import EntityClientBase


class EmployeeClient(EntityClientBase):
    entity_endpoint_base_url = '/management/employees/'

    def __init__(self, country_code='cl', **kwargs):
        super(EmployeeClient, self).__init__(**kwargs)
        self.entity_endpoint_base_url += country_code + '/'

    def is_work_day(self, work_day=None):
        return self.http_post_json(
            self.entity_endpoint_base_url + "_is-work-day",
            {'work_day': work_day} if work_day else {}
        )
