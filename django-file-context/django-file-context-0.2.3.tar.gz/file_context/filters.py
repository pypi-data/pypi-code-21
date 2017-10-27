# coding: utf-8
import rest_framework_filters as filters
from .models import (
    File,
)


class TaggitFilter(filters.FilterSet):

    tags = filters.BooleanFilter(name='tags', method='filter_tags')

    def filter_tags(self, qs, name, value):
        if not value:
            return qs
        values = value.split(',')
        if not values:
            return qs
        return qs.objects.filter(tags__name__in=values)


class FileFilter(TaggitFilter):

    class Meta:
        model = File
        fields = {
            'id': ['exact'],
            'name': ['exact', 'startswith', 'icontains'],
            'description': ['icontains']
        }
