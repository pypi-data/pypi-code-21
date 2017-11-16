# -*- coding:utf-8 -*-
from django.utils.module_loading import autodiscover_modules

from django_szuprefix.utils import modelutils

__author__ = 'denishuang'
from rest_framework import serializers, routers
router = routers.DefaultRouter()

def autodiscover():
    # print "autodiscover"
    autodiscover_modules('apis')

def register(package, resource, viewset):
    # print "%s/%s" % (package, resource)
    router.register("%s/%s" % (package, resource), viewset)

serializers.ModelSerializer.serializer_field_mapping.update({modelutils.JSONField: serializers.JSONField})
autodiscover()