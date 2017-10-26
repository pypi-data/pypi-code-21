# coding: utf-8
import rest_framework_filters as filters
from .models import (
    ProjectType,
    Project,
    TaskStatus,
    Task,
    Comment,
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


class ProjectTypeFilter(filters.FilterSet):

    class Meta:
        model = ProjectType
        fields = {
            'id': ['exact'],
            'code': ['exact', 'startswith', 'icontains'],
            'description': ['exact', 'startswith', 'icontains']
        }


class ProjectFilter(TaggitFilter):

    class Meta:
        model = Project
        fields = {
            'id': ['exact'],
            'name': ['exact', 'startswith', 'icontains'],
            'type': ['exact'],
            'responsible': ['exact'],
            'description': ['icontains'],
            'tags': ['exact'],
        }


class TaskStatusFilter(filters.FilterSet):

    class Meta:
        model = TaskStatus
        fields = {
            'id': ['exact'],
            'code': ['exact', 'startswith', 'icontains'],
            'description': ['exact', 'startswith', 'icontains'],
            'is_system_status': ['exact'],
            'is_closing_status': ['exact']
        }


class TaskFilter(TaggitFilter):

    class Meta:
        model = Task
        fields = {
            'id': ['exact'],
            'project': ['exact'],
            'parent': ['exact'],
            'responsible': ['exact'],
            'status': ['exact'],
            'name': ['exact', 'startswith', 'icontains'],
            'description': ['icontains'],
            'tags': ['exact'],
        }


class CommentFilter(filters.FilterSet):

    class Meta:
        model = Comment
        fields = {
            'id': ['exact'],
            'created_by': ['exact'],
            'task': ['exact'],
            'text': ['icontains']
        }
