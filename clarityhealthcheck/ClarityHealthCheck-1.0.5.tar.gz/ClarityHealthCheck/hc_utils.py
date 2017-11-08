import threading
import uuid
from django.core import cache as clarity_cache
from django.conf import settings
from django.db import connections
import vertica_python
import requests
import logging

def create_check_list():
    check_list={}
    if hasattr(settings,'CLARITY_HEALTHCHECK_URLS'):
        check_list["SERVICES"] = settings.CLARITY_HEALTHCHECK_URLS
    if hasattr(settings,'VERTICA_CONNECTION_INFO'):
        check_list["VERTICA"] = settings.VERTICA_CONNECTION_INFO
    if hasattr(settings,'DATABASES'):
        check_list["DATABASES"] = settings.DATABASES
    if hasattr(settings,'CACHES'):
        check_list["CACHES"]= settings.CACHES

    return check_list