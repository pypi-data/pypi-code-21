# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
from hashlib import md5

import logging
import geocoder
import django
import uuid

from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.loader import MigrationLoader
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.core.cache import cache

from user_agents import parse

from .models import Visitor

User = get_user_model()
logger = logging.getLogger('system')

"""
Thread Locals hack for easy access to current request from anywhere
"""
try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()


def get_current_request():
    return getattr(_thread_locals, 'request', None)


if sys.version_info[0] == 3:
    text_type = str
else:
    text_type = unicode


def get_cache_key(ua_string):
    if isinstance(ua_string, text_type):
        ua_string = ua_string.encode('utf-8')
    return ''.join(['django_user_agents.', md5(ua_string).hexdigest()])


def get_user_agent(request):
    ua_string = request.META.get('HTTP_USER_AGENT', '')
    key = get_cache_key(ua_string)
    user_agent = cache.get(key)
    if user_agent is None:
        user_agent = parse(ua_string)
        cache.set(key, user_agent)
    return user_agent


def get_and_set_user_agent(request):
    if hasattr(request, 'user_agent'):
        return request.user_agent

    request.user_agent = get_user_agent(request)
    return request.user_agent


def get_all_migrations_status():
    list_data = {'migrated_apps': '', 'unmigrated_apps': ''}
    connection = connections[DEFAULT_DB_ALIAS]
    connection.prepare_database()
    self = MigrationLoader(connection)
    self.load_disk()
    list_data['migrated_apps'] = self.migrated_apps
    executor = MigrationExecutor(connection)
    targets = executor.loader.graph.leaf_nodes()
    list_data['unmigrated_apps'] = set([app[0].app_label for app in executor.migration_plan(targets)])
    return list_data
    # executor.migrate(targets) for migrate model


def user_is_authenticated(user):
    if django.VERSION >= (1, 10):
        return user.is_authenticated
    else:
        return user.is_authenticated()


def process_user_agent_info(request):
    if hasattr(request, 'user') and user_is_authenticated(request.user):
        if request.user_agent.is_mobile:
            device_type = "Mobile"
        elif request.user_agent.is_tablet:
            device_type = "Tablet"
        elif request.user_agent.is_touch_capable:
            device_type = "Touch"
        elif request.user_agent.is_pc:
            device_type = "PC"
        elif request.user_agent.is_bot:
            device_type = "Bot"
        else:
            device_type = "Unknown"

        browser = request.user_agent.browser.family
        browser_version = request.user_agent.browser.version_string

        os_info = request.user_agent.os.family
        os_info_version = request.user_agent.os.version_string

        device_name = request.user_agent.device.family
        device_name_brand = request.user_agent.device.brand
        device_name_model = request.user_agent.device.model

        ipaddress = request.META.get("HTTP_X_FORWARDED_FOR", None)
        if ipaddress:
            ipaddress = ipaddress.split(", ")[0]
        else:
            ipaddress = request.META.get("REMOTE_ADDR", "")
        if not request.session.exists(request.session.session_key):
            request.session.create()
        session = Session.objects.get(session_key=request.session.session_key)

        if 'VISITOR_ID' in request.session.keys():
            user_uid = request.session.get('VISITOR_ID')
        else:
            user_uuid = uuid.uuid4()
            request.session['VISITOR_ID'] = user_uuid
            user_uid = request.session['VISITOR_ID']

        city = None
        state = None
        country = None
        latitude = None
        longitude = None
        try:
            if not request.POST['latitude'] == '':
                latitude = request.POST['latitude']
                longitude = request.POST['longitude']
                g = geocoder.google([latitude, longitude], method='reverse')
                city = g.city
                state = g.state_long
                country = g.country_long
            else:
                location = geocoder.ipinfo(ipaddress)
                if location:
                    city = location.city
                    state = location.state
                    country = location.country
        except Exception as e:
            pass
        username = request.user
        unique_computer = request.META.get("PROCESSOR_IDENTIFIER", None)
        visitor, created = Visitor.objects.get_or_create(
            ipaddress=ipaddress,
            user_uid=user_uid,
            browser=browser,
            browser_version=browser_version,
            os_info_version=os_info_version,
            os_info=os_info
        )
        visitor.name = username
        visitor.device_type = device_type
        visitor.browser = browser
        visitor.browser_version = browser_version
        visitor.os_info_version = os_info_version
        visitor.os_info = os_info
        visitor.device_name = device_name
        visitor.city = city
        visitor.state = state
        visitor.country = country
        visitor.device_name_brand = device_name_brand
        visitor.device_name_model = device_name_model
        visitor.unique_computer_processor = unique_computer
        visitor.session = session
        visitor.latitude = latitude
        visitor.longitude = longitude
        visitor.save()
    else:
        if request.user_agent.is_mobile:
            device_type = "Mobile"
        elif request.user_agent.is_tablet:
            device_type = "Tablet"
        elif request.user_agent.is_touch_capable:
            device_type = "Touch"
        elif request.user_agent.is_pc:
            device_type = "PC"
        elif request.user_agent.is_bot:
            device_type = "Bot"
        else:
            device_type = "Unknown"

        browser = request.user_agent.browser.family
        browser_version = request.user_agent.browser.version_string

        os_info = request.user_agent.os.family
        os_info_version = request.user_agent.os.version_string

        device_name = request.user_agent.device.family
        device_name_brand = request.user_agent.device.brand
        device_name_model = request.user_agent.device.model

        ipaddress = request.META.get("HTTP_X_FORWARDED_FOR", None)
        if ipaddress:
            ipaddress = ipaddress.split(", ")[0]
        else:
            ipaddress = request.META.get("REMOTE_ADDR", "")
        if not request.session.exists(request.session.session_key):
            request.session.create()
        session = Session.objects.get(session_key=request.session.session_key)
        city = None
        state = None
        country = None
        latitude = None
        longitude = None
        try:
            if not request.POST['latitude'] == '':
                latitude = request.POST['latitude']
                longitude = request.POST['longitude']
                g = geocoder.google([latitude, longitude], method='reverse')
                city = g.city
                state = g.state_long
                country = g.country_long
            else:
                location = geocoder.ipinfo(ipaddress)
                if location:
                    city = location.city
                    state = location.state
                    country = location.country
        except Exception as e:
            pass
        unique_computer = request.META.get("PROCESSOR_IDENTIFIER", None)

        if 'VISITOR_ID' in request.session.keys():
            user_uid = request.session.get('VISITOR_ID')
        else:
            user_uuid = uuid.uuid4()
            request.session['VISITOR_ID'] = user_uuid
            user_uid = request.session['VISITOR_ID']

        visitor, created = Visitor.objects.get_or_create(
            ipaddress=ipaddress,
            browser=browser,
            user_uid=user_uid,
            browser_version=browser_version,
            os_info_version=os_info_version,
            os_info=os_info
        )
        visitor.device_type = device_type
        visitor.browser = browser
        visitor.browser_version = browser_version
        visitor.os_info_version = os_info_version
        visitor.os_info = os_info
        visitor.device_name = device_name
        visitor.city = city
        visitor.state = state
        visitor.country = country
        visitor.device_name_brand = device_name_brand
        visitor.device_name_model = device_name_model
        visitor.unique_computer_processor = unique_computer
        visitor.session = session
        visitor.latitude = latitude
        visitor.longitude = longitude
        visitor.save()
    return 'Done'

