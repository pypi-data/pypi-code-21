# coding: utf-8
from rest_framework import routers
from .viewsets import (
    FileViewSet,
)


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'files', FileViewSet)
