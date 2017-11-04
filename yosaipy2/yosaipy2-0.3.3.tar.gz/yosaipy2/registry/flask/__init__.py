#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Response, request, Flask, Request
from flask import g, session
from yosaipy2.web.registry.abcs import WebRegistry
from yosaipy2.web import WebYosai
from yosaipy2.registry.flask.webregistry import FlaskWebRegistry
from typing import Callable, Dict, Optional
import json


def get_session_registry(create=False):
    # type: (bool) -> Optional[WebRegistry]
    if 'yosai_webregistry' not in session:
        if create:
            registry = FlaskWebRegistry()
            session['yosai_webregistry'] = registry
        else:
            registry = None
    else:
        saved_registry = str(session['yosai_webregistry'])
        if not isinstance(saved_registry, FlaskWebRegistry):
            registry = FlaskWebRegistry()
            registry.decode(json.loads(saved_registry))
        else:
            registry = saved_registry
    return registry


def init_flask(app, yosai):
    # type: (Flask, WebYosai, Callable[[Request], Dict]) -> None
    def before_request():
        registry = get_session_registry(create=True)
        yosai_context = WebYosai.context(yosai, registry)
        g.yosai_context = yosai_context
        g.yosai_context.__enter__()

    def after_request(response):
        # type:(Response) -> Response
        registry = WebYosai.get_current_webregistry()
        registry.webregistry_callback(request, response)
        session['yosai_webregistry'] = registry
        g.yosai_context.__exit__(None, None, None)
        return response

    app.before_request(before_request)
    app.after_request(after_request)
