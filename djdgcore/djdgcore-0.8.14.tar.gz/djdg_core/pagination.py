#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/8/3
 """
from __future__ import unicode_literals, absolute_import
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict


class SimplePageNumberPagination(PageNumberPagination):
    """
    按页数分页
    """
    page_query_param = 'page'
    page_size_query_param = 'limit'

    def get_paginated_response(self, data):
        count = self.page.start_index() if 0 == self.page.start_index() else self.page.end_index() - self.page.start_index() + 1
        return Response(
            OrderedDict([
                ('count', count),
                ('currPage', self.page.number),
                ('totalPage', self.page.paginator.num_pages),
                ('hasNext', self.page.has_next()),
                ('total', self.page.paginator.count),
                ('data', data),
                ('next', self.get_next_link()),
                ('previous', self.get_previous_link()),
            ])
        )
