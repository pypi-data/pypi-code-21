from django.db import connections
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.conf import settings

from ClarityHealthCheck.hc_utils import create_check_list
from ClarityHealthCheck.hc_classes import Service, HCEntityFactory

def check_status(request):

    status_list = {}

    checklist = create_check_list()

    for key, val in checklist.iteritems():
        obj = HCEntityFactory.createHCEntity(key, val)
        status_list[key] = obj.check_status()

    return JsonResponse(status_list, safe=False)

def reply_ping(request):
    return HttpResponse("pong")
