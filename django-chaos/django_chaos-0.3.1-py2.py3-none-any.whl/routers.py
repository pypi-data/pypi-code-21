# coding: utf-8
from rest_framework import routers
from file_context.viewsets import FileViewSet
from .viewsets import (
    ProjectTypeViewSet,
    ProjectViewSet,
    ProjectTemplateViewSet,
    TaskStatusViewSet,
    TaskViewSet,
    CommentViewSet,
    AllocationViewSet,
)


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'project-types', ProjectTypeViewSet)
router.register(r'task-status', TaskStatusViewSet, base_name='task-status')
router.register(r'templates', ProjectTemplateViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'allocations', AllocationViewSet, base_name='allocations')
router.register(r'files', FileViewSet)
