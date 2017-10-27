# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

import json

from tcell_agent.agent import TCellAgent, PolicyTypes
from tcell_agent.appsensor import params
from tcell_agent.appsensor.manager import app_sensor_manager
from tcell_agent.appsensor.meta import headers_from_environ
from tcell_agent.instrumentation.djangoinst.app import _default_charset as DEFAULT_CHARSET
from tcell_agent.sanitize.sanitize_utils import ensure_str_or_unicode


def django_meta(request):
    appsensor_meta = request._tcell_context.appsensor_meta
    appsensor_meta.set_raw_remote_address(request._tcell_context.raw_remote_addr)
    appsensor_meta.method = request.META.get("REQUEST_METHOD")
    appsensor_meta.user_agent_str = request.META.get("HTTP_USER_AGENT")
    appsensor_meta.location = request.build_absolute_uri()
    appsensor_meta.path = request.path
    appsensor_meta.route_id = request._tcell_context.route_id
    appsensor_meta.session_id = request._tcell_context.session_id
    appsensor_meta.user_id = request._tcell_context.user_id
    appsensor_meta.encoding = request.encoding or DEFAULT_CHARSET

    return appsensor_meta


def django_request_response_appsensor(django_response_class, request, response):
    if request._tcell_context.ip_blocking_triggered:
        return

    appsensor_policy = TCellAgent.get_policy(PolicyTypes.APPSENSOR)
    if appsensor_policy is None:
        return

    meta = django_meta(request)
    set_request(meta, request)
    meta.set_response(django_response_class, response)

    app_sensor_manager.send_appsensor_data(meta)


def set_request(meta, request):
    if meta.request_processed:
        return
    meta.request_processed = True

    request_len = 0

    try:
        request_len = int(request.META.get("CONTENT_LENGTH", 0))
    except:
        pass

    post_dict = {}
    request_json_body = None

    try:
        if request_len is not None and request_len > 0:
            post_dict = request.POST
            content_type = request.META.get("CONTENT_TYPE", "")
            if not content_type.startswith("multipart/form-data"):
                # Can't just say post as it may be PUT or maybe something else
                # We're going to make sure some crazy client didn't submit json by mistake
                request_body = request.body
                if request_len < 2000000 and len(request_body) < 2000000:
                    if content_type.startswith("application/json"):
                        request_json_body = request_body
                    else:
                        request_body = ensure_str_or_unicode(meta.encoding, request_body)
                        if request_body[0] == '{' or request_body[0] == '[':
                            try:
                                json.loads(request_body)
                                post_dict = {}
                                request_json_body = request_body
                            except ValueError:
                                pass
    except:
        pass

    meta.get_dict = request.GET
    meta.cookie_dict = request.COOKIES
    meta.headers_dict = headers_from_environ(request.META)
    meta.json_body_str = request_json_body
    meta.request_content_bytes_len = request_len

    filenames_dict = {}
    for param_name in (request.FILES or {}).keys():
        filenames_dict[param_name] = []
        for file_obj in request.FILES.getlist(param_name):
            filenames_dict[param_name].append(file_obj.name)

    meta.files_dict = params.flatten_clean(meta.encoding, filenames_dict)
    meta.post_dict = params.flatten_clean(meta.encoding, post_dict)
