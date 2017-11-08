#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/9/13
 """
from __future__ import unicode_literals, absolute_import
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework import mixins


class ListModelMixin(object):
    """
    List a queryset.
    """
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page_param = request.query_params.get('page')

        if page_param is not None:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class RetrieveWithForeignModelMixin(object):
    """
    Retrieve a model instance.
    """
    foreign_key = ''

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_queryset_with_foreign_key()
        serializer = self.get_serializer(obj, many=True)
        return Response(serializer.data)

    def get_queryset_with_foreign_key(self):
        queryset = self.filter_queryset(self.get_queryset())
        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )
        foreign_key_id = '{0}_id'.format(self.foreign_key)
        filter_kwargs = {foreign_key_id: self.kwargs[lookup_url_kwarg]}
        obj = queryset.filter(**filter_kwargs)
        return obj


class LockMixin(object):
    """
    锁
    """
    def get_object(self, select_for_update=False, queryset=None):
        if not queryset:
            queryset = self.filter_queryset(self.get_queryset())
        if select_for_update:
            queryset = queryset.select_for_update()

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj
