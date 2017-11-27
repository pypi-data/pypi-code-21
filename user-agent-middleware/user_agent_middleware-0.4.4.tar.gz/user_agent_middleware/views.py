# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import geocoder
import uuid

from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.sessions.models import Session


from .utils import user_is_authenticated
from .models import Visitor


class GetUserAgentInfo(APIView):
    permission_classes = []

    def get(self, request, *args, **kwargs):
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
                user_uuid = str(uuid.uuid4())
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
        return Response({'status': 'OK'}, status=200)