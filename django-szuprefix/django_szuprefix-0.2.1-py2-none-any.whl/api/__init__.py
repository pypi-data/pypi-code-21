# -*- coding:utf-8 -*-
from django.utils.module_loading import autodiscover_modules

__author__ = 'denishuang'
from rest_framework import routers
router = routers.DefaultRouter()

def autodiscover():
    # print "autodiscover"
    autodiscover_modules('apis')

def register(package, resource, viewset):
    # print "%s/%s" % (package, resource)
    router.register("%s/%s" % (package, resource), viewset)

autodiscover()