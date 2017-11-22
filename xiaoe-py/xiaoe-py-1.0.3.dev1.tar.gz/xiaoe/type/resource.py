from .base import BaseData, OptionalDict


class ResourceQueryData(BaseData):
    def __init__(self, order_by=None, page_index=None, page_size=None,
                 resource_types=None, user_id=None, state=None, is_started=None):
        self.data = OptionalDict()
        self.data['order_by'] = order_by
        self.data['page_index'] = page_index
        self.data['page_size'] = page_size
        self.data['resource_types'] = resource_types
        self.data['user_id'] = user_id
        self.data['state'] = state
        self.data['is_started'] = is_started


class ResourceQueryByColumnData(BaseData):
    def __init__(self, product_id=None, order_by=None, page_index=None, page_size=None,
                 resource_types=None, user_id=None):
        self.data = OptionalDict()
        self.data['product_id'] = product_id
        self.data['order_by'] = order_by
        self.data['page_index'] = page_index
        self.data['page_size'] = page_size
        self.data['resource_types'] = resource_types
        self.data['user_id'] = user_id


class ResourceDetailQueryData(BaseData):
    def __init__(self, resource_id=None, user_id=None):
        self.data = OptionalDict()
        self.data['resource_id'] = resource_id
        self.data['user_id'] = user_id