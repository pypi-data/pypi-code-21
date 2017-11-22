from .base import BaseData, OptionalDict


class ColumnQueryData(BaseData):
    def __init__(self, order_by=None, page_index=None, page_size=None,
                 user_id=None, state=None):
        self.data = OptionalDict()
        self.data['order_by'] = order_by
        self.data['page_index'] = page_index
        self.data['page_size'] = page_size
        self.data['user_id'] = user_id
        self.data['state'] = state


class ColumnRoleQueryData(BaseData):
    def __init__(self, order_by=None, page_index=None, page_size=None, user_id=None, state=None):
        self.data = OptionalDict()
        self.data['order_by'] = order_by
        self.data['page_index'] = page_index
        self.data['page_size'] = page_size
        self.data['user_id'] = user_id
        self.data['state'] = state


class ColumnDetailQueryData(BaseData):
    def __init__(self, product_id=None, user_id=None):
        self.data = OptionalDict()
        self.data['product_id'] = product_id
        self.data['user_id'] = user_id
