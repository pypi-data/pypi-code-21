# -*- coding: utf-8 -*-


class QueryOptions:  # pylint: disable=too-few-public-methods
    """
    Crate with settings for db query
    """
    query = None
    sort = None
    page = 1
    limit = None
    projection = None
    id_field = None

    def __init__(self, query=None, sort=None, page=1, limit=None, projection=None, id_field=None):  # pylint: disable=too-many-arguments
        self.query = query
        self.sort = sort
        self.page = page
        self.limit = limit
        self.projection = projection
        self.id_field = id_field

    @property
    def offset(self):
        return (self.page - 1) * (self.limit or 0)

    def __repr__(self):
        return '<{} p:{} l:{} q:{} s:{}>'.format(self.__class__.__name__, self.page, self.limit, self.query, self.sort)
